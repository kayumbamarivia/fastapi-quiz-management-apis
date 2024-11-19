from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.questions import router as question_router

app = FastAPI(
    title="My QUIZ FastAPI Application",
    description="This is an application for generating questions and answers RESTFUL APIS", 
    version="1.0.0" 
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(question_router, tags=["Quiz Questions"])
