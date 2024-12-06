from fastapi import FastAPI, HTTPException
import time
import random

app = FastAPI()

# Simulate job storage
jobs = {}

# Get the status of a job by job_id
@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        jobs[job_id] = {
            "start_time": time.time(),
            "duration": random.randint(15, 30)  # Random job duration between 15-30 seconds
        }
    
    job = jobs[job_id]
    elapsed_time = time.time() - job["start_time"]
    
    # Check completion first
    if elapsed_time >= job["duration"]:
        return {"result": "completed"}
    
    # Then check for random errors for pending jobs
    if random.random() < 0.15:  # 15% chance of error
        return {"result": "error"}
    
    # Otherwise return pending
    return {"result": "pending"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
