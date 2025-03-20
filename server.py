from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Optional
import os
import shutil
import uuid
from datetime import datetime
import git
import tempfile

from models.github_request import GitHubRequest
from services.analysis_service import AnalysisService

app = FastAPI(
    title="AngularJS to React Migration API",
    description="API for handling AngularJS to React migration through GitHub URLs and ZIP files",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory if it doesn't exist
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
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

async def trigger_analysis(project_dir: str):
    """Trigger project analysis in the background"""
    await AnalysisService.start_analysis(project_dir)

@app.get("/")
async def root():
    return {"message": "Welcome to AngularJS to React Migration API"}

@app.post("/api/v1/migration/github")
async def migrate_from_github(request: GitHubRequest):
    github_url = request.github_url
    try:
        project_id = generate_project_id()
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the repository
            git.Repo.clone_from(github_url, temp_dir)
            # Save to output directory
            project_dir = await save_upload_to_output(project_id, temp_dir, is_dir=True)
            
            # Trigger analysis in the background
            await trigger_analysis(project_dir)
        
        return {
            "status": "success",
            "message": "GitHub repository cloned successfully and analysis started",
            "project_id": project_id,
            "github_url": github_url,
            "output_directory": project_dir
        }
    except git.GitCommandError as e:
        raise HTTPException(status_code=400, detail=f"Git error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/migration/zip")
async def migrate_from_zip(file: UploadFile):
    try:
        project_id = generate_project_id()
        
        # Create temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Save to output directory
            project_dir = await save_upload_to_output(project_id, temp_path)
            
            # Trigger analysis in the background
            await trigger_analysis(project_dir)
            
            return {
                "status": "success",
                "message": "ZIP file uploaded successfully and analysis started",
                "project_id": project_id,
                "filename": file.filename,
                "output_directory": project_dir
            }
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)