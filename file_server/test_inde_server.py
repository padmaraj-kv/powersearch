from fastapi import FastAPI, Request
import asyncio
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, API!"}

@app.post("/files")
async def create_file(request: Request):
    data = await request.json()
    print(f"[LOG] Received file: {data}") 
    await asyncio.sleep(10)
    return {"message": "File created successfully"}

@app.delete("/files")
async def delete_file(request: Request):
    data = await request.json()
    print(f"[LOG] Received file: {data}") 
    await asyncio.sleep(10)
    return {"message": "File deleted successfully"}

@app.get("/files")
async def search_files(path: str):
    print(f"[LOG] Searching for files with path: {path}")
    return {"message": "Files searched successfully"}

if __name__ == "__main__":
    uvicorn.run(app, port=5001)