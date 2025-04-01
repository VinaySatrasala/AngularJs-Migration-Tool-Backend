import os
import shutil
import asyncio
import psutil
from typing import Optional

# Base directories, to be imported from a config file in a real implementation
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

async def terminate_git_processes() -> None:
    """Terminate any Git processes before cleanup"""
    for process in psutil.process_iter(['pid', 'name']):
        if 'git' in process.info['name'].lower():
            try:
                process.terminate()
            except (psutil.NoSuchProcess, PermissionError):
                pass  # Process already closed or permission denied

async def cleanup_directory(base_dir: str, dir_id: str) -> None:
    """Clean up a directory given a base directory and ID"""
    try:
        # Ensure response is fully sent before cleanup starts
        await asyncio.sleep(1)
        
        dir_path = os.path.join(base_dir, dir_id)
        if dir_id and os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
                
                # If directory still exists after rmtree, try force removal
                if os.path.exists(dir_path):
                    if os.name == 'nt':  # Windows
                        os.system(f'rmdir /S /Q "{dir_path}"')
                    else:  # Unix/Linux
                        os.system(f'rm -rf "{dir_path}"')
            except Exception as e:
                print(f"Error during directory removal: {str(e)}")
    except Exception as e:
        print(f"Error during directory cleanup: {str(e)}")

async def cleanup_file(file_path: Optional[str]) -> None:
    """Clean up a file given its path"""
    try:
        # Ensure response is fully sent before cleanup starts
        await asyncio.sleep(1)
        
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Error during file cleanup: {str(e)}")

async def cleanup_uploads(project_id: str) -> None:
    """Clean up project directory in uploads folder"""
    await terminate_git_processes()
    await cleanup_directory(UPLOAD_DIR, project_id)

async def cleanup_outputs(project_id: str) -> None:
    """Clean up output directory"""
    await cleanup_directory(OUTPUT_DIR, project_id)

async def cleanup_zip(zip_path: str) -> None:
    """Clean up ZIP file"""
    await cleanup_file(zip_path)

async def cleanup_temp_file(temp_path: str) -> None:
    """Clean up temporary file"""
    await cleanup_file(temp_path)

async def perform_full_cleanup(project_id: str, zip_path: Optional[str] = None, temp_path: Optional[str] = None) -> None:
    """Perform a full cleanup of all resources"""
    await terminate_git_processes()
    await cleanup_uploads(project_id)
    await cleanup_outputs(project_id)
    
    if zip_path:
        await cleanup_zip(zip_path)
    
    if temp_path:
        await cleanup_temp_file(temp_path)