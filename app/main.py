import uvicorn
from app_server import app  # 'app' should be the FastAPI instance

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)