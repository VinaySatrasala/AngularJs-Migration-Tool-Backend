from fastapi import APIRouter, HTTPException, UploadFile, BackgroundTasks
from starlette.responses import FileResponse
import tempfile
import shutil
import os
import git
from datetime import datetime
import uuid
import zipfile
from models.github_request import GitHubRequest
from services.analysis_service import AnalysisService
import asyncio

router = APIRouter(prefix="/api/v1/migration", tags=["migration"])

# Create output directory if it doesn't exist
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_project_id():
    """Generate a unique project ID with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"

async def save_upload_to_output(project_id: str, source_path: str, is_dir: bool = False):
    """Save uploaded content to output directory"""
    project_dir = os.path.join(OUTPUT_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    
    if is_dir:
        shutil.copytree(source_path, project_dir, dirs_exist_ok=True)
    else:
        shutil.copy2(source_path, project_dir)
    
    return project_dir

def create_zip_file(output_dir: str, project_id: str) -> str:
    """Create a ZIP file of the migrated project"""
    zip_path = os.path.join(OUTPUT_DIR, f"{project_id}_migrated.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Get the react_output directory path
        react_output_dir = os.path.join(output_dir, "react_output")
        
        # Walk through the react_output directory and add files to zip
        for root, _, files in os.walk(react_output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, react_output_dir)
                zipf.write(file_path, arcname)
    return zip_path

def cleanup_files(project_dir: str, zip_path: str):
    """Clean up project directory and zip file"""
    try:
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        if os.path.exists(zip_path):
            os.remove(zip_path)
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

@router.post("/github")
async def migrate_from_github(request: GitHubRequest):
    github_url = request.github_url
    project_dir = None
    zip_path = None
    try:
        project_id = generate_project_id()
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the repository
            git.Repo.clone_from(github_url, temp_dir)
            # Save to output directory
            project_dir = await save_upload_to_output(project_id, temp_dir, is_dir=True)
            
            # Run analysis and wait for completion
            result = await AnalysisService.analyze_project(project_dir, project_id)
            
            # Create ZIP file of the migrated project
            zip_path = create_zip_file(result["output_dir"], project_id)
            
            # Return the ZIP file
            response = FileResponse(
                zip_path,
                media_type='application/zip',
                filename=f"{project_id}_migrated.zip"
            )
            
            # Add a background task to clean up files after sending response
            response.background = BackgroundTasks()
            response.background.add_task(cleanup_files, project_dir, zip_path)
            
            return response
            
    except git.GitCommandError as e:
        if project_dir or zip_path:
            cleanup_files(project_dir, zip_path)
        raise HTTPException(status_code=400, detail=f"Git error: {str(e)}")
    except Exception as e:
        if project_dir or zip_path:
            cleanup_files(project_dir, zip_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/zip")
async def migrate_from_zip(file: UploadFile):
    project_dir = None
    zip_path = None
    try:
        project_id = generate_project_id()
        
        # Create temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Save to output directory
            project_dir = os.path.join(OUTPUT_DIR, project_id)
            os.makedirs(project_dir, exist_ok=True)

            # Extract ZIP to project directory
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                zip_ref.extractall(project_dir)
            
            # Run analysis and wait for completion
            result = await AnalysisService.analyze_project(project_dir, project_id)
            
            # Create ZIP file of the migrated project
            zip_path = create_zip_file(result["output_dir"], project_id)
            
            # Return the ZIP file
            response = FileResponse(
                zip_path,
                media_type='application/zip',
                filename=f"{project_id}_migrated.zip"
            )
            
            # Add a background task to clean up files after sending response
            response.background = BackgroundTasks()
            response.background.add_task(cleanup_files, project_dir, zip_path)
            
            return response
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        if project_dir or zip_path:
            cleanup_files(project_dir, zip_path)
        raise HTTPException(status_code=500, detail=str(e))



