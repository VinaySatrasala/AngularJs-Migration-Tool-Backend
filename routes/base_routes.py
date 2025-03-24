from fastapi import APIRouter

router = APIRouter(tags=["base"])

@router.get("/")
async def root():
    return {
        "message": "Welcome to AngularJS to React Migration API",
        "endpoints": {
            "github_migration": "/api/v1/migration/github",
            "zip_migration": "/api/v1/migration/zip",
            "migration_status": "/api/v1/migration/status/{project_id}"
        }
    }
