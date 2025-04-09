from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routes.base_routes import router as base_router
from routes.migration_routes import router as migration_router

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.db_cleanup_service import CleanupService
from config.db_config import get_db

app = FastAPI(
    title="AngularJS to React Migration API",
    description="API for handling AngularJS to React migration through GitHub URLs and ZIP files",
    version="1.0.0"
)

scheduler = AsyncIOScheduler()
# Setup cleanup job
def cleanup_job():
    db = next(get_db())
    try:
        CleanupService.cleanup_old_records(db)
    finally:
        db.close()

# Schedule cleanup every 6 hours
scheduler.add_job(
    cleanup_job,
    trigger=IntervalTrigger(hours=6),
    id='cleanup_job',
    name='Database cleanup every 6 hours',
    replace_existing=True
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(base_router)
app.include_router(migration_router)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)