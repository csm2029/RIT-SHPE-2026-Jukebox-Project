from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow React to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Jukebox backend is running!"}

@app.get("/test")
def test():
    return {"status": "success", "data": "Hello from backend"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)