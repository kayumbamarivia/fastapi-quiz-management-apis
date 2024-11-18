from fastapi import FastAPI
from routes.questions import router


app = FastAPI(
    title="My QUIZ FastAPI Application",
    description="This is an application for generating questions and answers RESTFUL APIS", 
    version="1.0.0" 
)

app.include_router(router)