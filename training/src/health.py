from fastapi import FastAPI, HTTPException
import psutil
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    try:
        return {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "gpu_info": get_gpu_info()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

def get_gpu_info():
    try:
        import torch
        return {
            "gpu_available": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        }
    except:
        return {"gpu_available": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 