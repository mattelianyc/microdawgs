from typing import Dict, Any, Optional, List
import asyncio
import redis
import json
import logging
import uuid
from datetime import datetime
from ..config import Settings
from shared.models.request_schemas import BatchProcessingRequest
from shared.models.enums import JobStatus

logger = logging.getLogger(__name__)

class JobQueue:
    """Handle job queueing and status tracking"""
    def __init__(self):
        self.settings = Settings()
        self.redis = redis.from_url(self.settings.redis_url)
        self.processing_queue = "processing_queue"
        self.results_key = "job_results:{job_id}"
        self.status_key = "job_status:{job_id}"

    async def submit_job(
        self,
        request: BatchProcessingRequest
    ) -> str:
        """Submit job to processing queue"""
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "request": request.dict(),
            "status": JobStatus.PENDING,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Store job data
        self.redis.set(
            self.status_key.format(job_id=job_id),
            json.dumps(job_data)
        )
        
        # Add to processing queue
        self.redis.lpush(
            self.processing_queue,
            json.dumps({"job_id": job_id})
        )
        
        return job_id

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and progress"""
        status_data = self.redis.get(
            self.status_key.format(job_id=job_id)
        )
        
        if not status_data:
            return None
            
        return json.loads(status_data)

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[float] = None,
        result: Optional[Dict[str, Any]] = None
    ):
        """Update job status and progress"""
        status_key = self.status_key.format(job_id=job_id)
        
        # Get current status
        current_data = self.redis.get(status_key)
        if not current_data:
            return
            
        job_data = json.loads(current_data)
        
        # Update status
        job_data.update({
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        if progress is not None:
            job_data["progress"] = progress
            
        if result is not None:
            job_data["result"] = result
            
        # Store updated status
        self.redis.set(status_key, json.dumps(job_data))

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel pending or processing job"""
        status_key = self.status_key.format(job_id=job_id)
        
        # Get current status
        current_data = self.redis.get(status_key)
        if not current_data:
            return False
            
        job_data = json.loads(current_data)
        
        # Check if job can be cancelled
        if job_data["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
            return False
            
        # Update status to cancelled
        job_data.update({
            "status": JobStatus.CANCELLED,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        # Store updated status
        self.redis.set(status_key, json.dumps(job_data))
        
        return True

    async def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old job data"""
        cutoff = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        # Scan for old jobs
        for key in self.redis.scan_iter("job_status:*"):
            try:
                job_data = json.loads(self.redis.get(key))
                created_at = datetime.fromisoformat(
                    job_data["created_at"]
                ).timestamp()
                
                if created_at < cutoff:
                    # Remove job data
                    self.redis.delete(key)
                    self.redis.delete(
                        self.results_key.format(job_id=job_data["job_id"])
                    )
                    
            except Exception as e:
                logger.error(f"Job cleanup failed: {str(e)}") 