from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import os
import time
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from app.data_handler import runcalc,load_data,process_output  # Import the new function
from app.tograph import getGraph
app = FastAPI()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://www.quantabricks.xyz"],  # Replace with your frontend URL(s)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

UPLOAD_FOLDER = "./uploaded_files"
RESULT_FOLDER = "./results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

tasks_status = {}

class TaskStatus(BaseModel):
    status: str
    result: str = None

@app.post("/upload/")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
             
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

                  
    task_id = f"task_{int(time.time())}"
    tasks_status[task_id] = "pending"

    background_tasks.add_task(process_file, task_id, file_path)

    return {"task_id": task_id}

async def process_file(task_id: str, file_path: str):
    try:
        tasks_status[task_id] = "on-going"
        # Run the simulation here
        data = load_data(file_path)  # Use the new function

        getGraph(data)
        #Run the xTB calculation
        #runStatus = runcalc(RESULT_FOLDER+f"/{task_id}")
        runStatus = "error"
        data = process_output(task_id, data)  # Call the new function
                
        result = {"processed": True, "data": data}  # 模拟处理的结果
        result_path = os.path.join(RESULT_FOLDER, f"{task_id}_result.json")

        with open(result_path, "w") as f:
            json.dump(result, f)

        if (runStatus =="Finished"): tasks_status[task_id] = "finished"
        tasks_status[task_id] = {"status": "finished", "result": result_path}
    except Exception as e:
        tasks_status[task_id] = {"status": "error", "error": str(e)}

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks_status:
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    status = tasks_status[task_id]
    if isinstance(status, dict) and status.get("status") == "finished":
        with open(status["result"], "r") as f:
            result_data = json.load(f)
        return {"status": "finished", "result": result_data}
    return {"status": status}

@app.get("/traj/{task_id}")
async def download_file(task_id: str):
    file_path = f"./results/{task_id}/opt.xyz"
    print(file_path)
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"error": "File not found"}
        )
    
    return FileResponse(
        path=file_path,
        filename=f"optimization_{task_id}.xyz",
        media_type="application/octet-stream"
    )


