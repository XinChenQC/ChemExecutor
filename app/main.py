from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import os
import time
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from app.data_handler import load_data,process_returnData  # Import the new function
from app.tograph import compGraph_init,compGraph_run

import shutil #zip
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
        print(data)
        # compG is computational graph
        compG = compGraph_init(data)        
        
        runStatus =  compGraph_run(compG, task_id)
        runStatus = "error"
        #data = process_returnData(DataReturns, data)  # Process return data
                
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

@app.get("/download/{task_id}")
async def download_file(task_id: str):
    file_path = os.path.join('/home/xchen/Work/fastAPI/temp/', task_id)
    zip_path = os.path.join('/home/xchen/Work/fastAPI/temp/', f"{task_id}.zip")
    print(zip_path)
    try:
        shutil.make_archive(file_path, 'zip', file_path)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create zip file: {str(e)}"}
        )

    if not os.path.exists(zip_path):
        return JSONResponse(
            status_code=404,
            content={"error": "File not found"}
        )
    
    return FileResponse(
        path=zip_path,
        filename=f"{task_id}_results.zip",
        media_type="application/zip"
    )


