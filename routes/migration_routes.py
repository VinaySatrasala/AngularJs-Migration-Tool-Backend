from fastapi import APIRouter, HTTPException, UploadFile, BackgroundTasks, Depends
from starlette.responses import FileResponse, Response
import tempfile
import shutil
import os
import git
from datetime import datetime
import uuid
import zipfile
from typing import Dict, Any, Optional

from models.TargetRequest import TargetRequest
from models.github_request import GitHubRequest
from services.analysis_service import AnalysisService
from services.db_service import MigrationDBService 
from config.db_config import get_db
from utils.cleanup_utils import (
    cleanup_uploads, 
    cleanup_outputs, 
    cleanup_zip, 
    cleanup_temp_file,
    perform_full_cleanup
)


router = APIRouter(prefix="/api/v1/migrator", tags=["migration"])

# Create output directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_project_id() -> str:
    """Generate a unique project ID with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"


async def save_upload_to_output(project_id: str, source_path: str, is_dir: bool = False) -> str:
    """Save uploaded content to output directory"""
    project_dir = os.path.join(UPLOAD_DIR, project_id)
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


@router.post("/github", response_class=FileResponse)
async def migrate_from_github(request: GitHubRequest, background_tasks: BackgroundTasks) -> Response:
    github_url = request.github_url
    project_id = generate_project_id()
    project_dir = None
    zip_path = None
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the repository
            git.Repo.clone_from(github_url, temp_dir)
            # Save to output directory
            project_dir = await save_upload_to_output(project_id, temp_dir, is_dir=True)
            
            # Run analysis and wait for completion
            result = await AnalysisService.migrate_project(project_dir, project_id)
            
            # Create ZIP file of the migrated project
            zip_path = create_zip_file(result["output_dir"], project_id)
            
            # Return the ZIP file
            response = FileResponse(
                zip_path,
                media_type='application/zip',
                filename=f"{project_id}_migrated.zip"
            )
            
            # Add a background task to clean up files after sending response
            background_tasks.add_task(perform_full_cleanup, project_id, zip_path)
            
            return response
            
    except git.GitCommandError as e:
        await perform_full_cleanup(project_id, zip_path)
        raise HTTPException(status_code=400, detail=f"Git error: {str(e)}")
    except Exception as e:
        await perform_full_cleanup(project_id, zip_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zip", response_class=FileResponse)
async def migrate_from_zip(file: UploadFile, background_tasks: BackgroundTasks) -> Response:
    project_id = generate_project_id()
    project_dir = None
    zip_path = None
    temp_path = None
    
    try:
        # Create temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            # Process the upload in chunks to avoid memory issues with large files
            chunk_size = 1024 * 1024  # 1MB chunks
            while chunk := await file.read(chunk_size):
                temp_file.write(chunk)
        
        # Save to output directory
        project_dir = os.path.join(UPLOAD_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)

        # Extract ZIP to project directory
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(project_dir)
        
        # Run analysis and wait for completion
        result = await AnalysisService.migrate_project(project_dir, project_id)
        
        # Create ZIP file of the migrated project
        zip_path = create_zip_file(result["output_dir"], project_id)
        
        # Return the ZIP file
        response = FileResponse(
            zip_path,
            media_type='application/zip',
            filename=f"{project_id}_migrated.zip"
        )
        
        # Add a background task to clean up all files after sending response
        background_tasks.add_task(perform_full_cleanup, project_id, zip_path, temp_path)
        
        return response
            
    except zipfile.BadZipFile:
        await perform_full_cleanup(project_id, zip_path, temp_path)
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except Exception as e:
        await perform_full_cleanup(project_id, zip_path, temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zip/analyze", response_model=Dict[str, Any])
async def analyze_zip(file: UploadFile, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    project_id = generate_project_id()
    project_dir = None
    temp_path = None
    
    try:
        # Create temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            # Process the upload in chunks to avoid memory issues with large files
            chunk_size = 1024 * 1024  # 1MB chunks
            while chunk := await file.read(chunk_size):
                temp_file.write(chunk)
        
        # Save to output directory
        project_dir = os.path.join(UPLOAD_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)

        # Extract ZIP to project directory
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(project_dir)
        
        # Run analysis and wait for completion
        result = await AnalysisService.generate_target_structure(project_dir, project_id)
        
        # Add a background task to clean up files after sending response
        background_tasks.add_task(cleanup_uploads, project_id)
        background_tasks.add_task(cleanup_temp_file, temp_path)
        
        return result
    
    except zipfile.BadZipFile:
        await perform_full_cleanup(project_id, temp_path=temp_path)
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except Exception as e:
        await perform_full_cleanup(project_id, temp_path=temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/github/analyze", response_model=Dict[str, Any])
async def analyze_github(request: GitHubRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    github_url = request.github_url
    project_id = generate_project_id()
    project_dir = None
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the repository
            git.Repo.clone_from(github_url, temp_dir)
            # Save to output directory
            project_dir = await save_upload_to_output(project_id, temp_dir, is_dir=True)
            
            # Run analysis and wait for completion
            result = await AnalysisService.generate_target_structure(project_dir, project_id)
            
            # Add a background task to clean up files after sending response
            background_tasks.add_task(cleanup_uploads, project_id)
            
            return result

    except git.GitCommandError as e:
        await cleanup_uploads(project_id)
        raise HTTPException(status_code=400, detail=f"Git error: {str(e)}")
    except Exception as e:
        await cleanup_uploads(project_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/migrate", response_class=FileResponse)
async def migrate(request: TargetRequest, background_tasks: BackgroundTasks) -> Response:
    project_id = request.project_id
    target_structure = request.target_structure
    changes = request.changes
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    zip_path = None
    
    try:
        result = await AnalysisService.migrate_from_target(project_id, target_structure, changes)
        
        # Create ZIP file of the migrated project
        zip_path = create_zip_file(result["output_dir"], project_id)
        
        # Return the ZIP file
        response = FileResponse(
            zip_path,
            media_type='application/zip',
            filename=f"{project_id}_migrated.zip"
        )
        
        # Add a background task to clean up files after sending response
        background_tasks.add_task(perform_full_cleanup, project_id, zip_path)
        
        return response
    
    except FileNotFoundError:
        await perform_full_cleanup(project_id, zip_path)
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    except Exception as e:
        await perform_full_cleanup(project_id, zip_path)
        raise HTTPException(status_code=500, detail=str(e))