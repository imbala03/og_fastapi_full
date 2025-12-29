
import uvicorn

if __name__ == "__main__":
    # Listen on all interfaces so devices on the same WiFi can access the API
    # From Android physical phone, use: http://192.168.1.9:8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
