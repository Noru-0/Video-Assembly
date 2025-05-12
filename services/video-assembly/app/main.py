from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.assembly import router as assembly_router  # Import the router from assembly.py
from app.routes.health import router as health_router  # Import the health check router
import os

app = FastAPI(title="Video Assembly Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the routes defined in assembly.py
app.include_router(assembly_router, prefix="/video-assembly", tags=["assembly"])
# Include the health check route
app.include_router(health_router, prefix="/video-assembly", tags=["health"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
    