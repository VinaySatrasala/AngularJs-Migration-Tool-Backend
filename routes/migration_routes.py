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
import psutil
from sqlalchemy.orm import Session
from services.db_service import MigrationDBService 
from config.db_config import get_db


router = APIRouter(prefix="/api/v1/migration", tags=["migration"])

# Create output directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_project_id():
    """Generate a unique project ID with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"

async def save_upload_to_output(project_id: str, source_path: str, is_dir: bool = False):
    """Save uploaded content to output directory"""
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    
    if is_dir:
        shutil.copytree(source_path, project_dir, dirs_exist_ok=True)
    else:
        shutil.copy2(source_path, project_dir)
    
    return project_dir

def create_zip_file(UPLOAD_DIR: str, project_id: str) -> str:
    """Create a ZIP file of the migrated project"""
    zip_path = os.path.join(UPLOAD_DIR, f"{project_id}_migrated.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Get the react_output directory path
        react_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "react_output")
        
        # Walk through the react_output directory and add files to zip
        for root, _, files in os.walk(react_UPLOAD_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, react_UPLOAD_DIR)
                zipf.write(file_path, arcname)
    return zip_path

def cleanup_files(project_dir: str, zip_path: str):
    """Clean up project directory, output directory, and zip file"""
    try:
        # Terminate any Git processes before cleanup
        for process in psutil.process_iter(['pid', 'name']):
            if 'git' in process.info['name'].lower():
                try:
                    process.terminate()
                except psutil.NoSuchProcess:
                    pass  # Process already closed

        # Remove project directory
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir, ignore_errors=True)

        # Remove generated zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)

        # Remove output directory
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
            os.makedirs(OUTPUT_DIR, exist_ok=True)  # Recreate it after cleanup

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
            project_dir = os.path.join(UPLOAD_DIR, project_id)
            os.makedirs(project_dir, exist_ok=True)

            # Extract ZIP to project directory
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                zip_ref.extractall(project_dir)
            
            # Run analysis and wait for completion
            result = await AnalysisService.analyze_project(project_dir, project_id)
            
            # Create ZIP file of the migrated project
            zip_path = create_zip_file(result["UPLOAD_DIR"], project_id)
            
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

# @router.get("/analysis/{project_id}")
# async def get_project_analysis(project_id: str, db: Session = next(get_db())):
#     """Fetch project analysis data by project_id"""
#     analysis = MigrationDBService.get_analysis(db, project_id)
#     if not analysis:
#         raise HTTPException(status_code=404, detail="Project analysis not found")
#     return analysis

# @router.get("/target-structure/{project_id}")
# async def get_target_structure(project_id: str, db: Session = next(get_db())):
#     """Fetch target structure data by project_id"""
#     structure = MigrationDBService.get_target_structure(db, project_id)
#     if not structure:
#         raise HTTPException(status_code=404, detail="Target structure not found")
#     return structure
