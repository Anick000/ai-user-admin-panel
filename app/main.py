from fastapi import FastAPI
from app.api.user_routes import router as user_router
from app.api.agent_routes import router as agent_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="MCP User Management API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# REST API routes
app.include_router(user_router)
app.include_router(agent_router)



@app.get("/")
def root():
    return {"message": "User API running"}
