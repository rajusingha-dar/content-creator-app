"""
Simple script to run the application using Uvicorn directly.
This is an alternative to running 'python -m app.main'
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Content Creator App...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)