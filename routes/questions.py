from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dto.responses import QuestionResponse, ChoiceBase, QuestionBase, SucessResponse
from config.database import engine, SessionLocal
from sqlalchemy.orm import Session
from models.questions import Base, Choices, Questions
from utils.auth import decode_access_token

router = APIRouter()

NOT_FOUND = "Question not found" 
security = HTTPBearer()

def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security)):
    token = authorization.credentials
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return username

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/")
def greet():
    return {"message": "Hello, Fast People!"}

@router.post("/questions/add", response_model=QuestionResponse)
async def create_question(q: QuestionBase, db: db_dependency, current_user: str = Depends(get_current_user)):
    db_question = Questions(question_text=q.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    for c in q.choices:
        db_choice = Choices(choice_text=c.choice_text, is_correct=c.is_correct, question_id=db_question.id)
        db.add(db_choice)
        db.commit()
    return QuestionResponse(question_text=db_question.question_text, 
                            choices=[ChoiceBase(choice_text=c.choice_text, is_correct=c.is_correct) 
                                     for c in db_question.choices])

@router.get("/questions", response_model=List[QuestionResponse])
async def get_questions(db: db_dependency, current_user: str = Depends(get_current_user)):
    db_questions = db.query(Questions).all()
    return [
        QuestionResponse(
            id=q.id,
            question_text=q.question_text, 
            choices=[ChoiceBase(id=c.id, choice_text=c.choice_text, is_correct=c.is_correct) for c in q.choices])
        for q in db_questions
        ]

@router.get("/questions/{q_id}", response_model=QuestionResponse)
async def get_question_by_id(q_id: int, db: db_dependency, current_user: str = Depends(get_current_user)):
    db_question = db.query(Questions).filter(Questions.id==q_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return QuestionResponse(
        id=db_question.id,
        question_text=db_question.question_text,
        choices=[ChoiceBase(id=c.id, choice_text=c.choice_text, is_correct=c.is_correct) for c in db_question.choices]
    )
    
@router.put("/questions/{q_id}/edit", response_model=QuestionResponse)
async def update_question_by_id(q_id: int, q: QuestionBase, db: db_dependency, current_user: str = Depends(get_current_user)):
    db_question = db.query(Questions).filter(Questions.id==q_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    
    db_question.question_text = q.question_text
    db.commit()
    db.refresh(db_question)
    db.query(Choices).filter(Choices.question_id==db_question.id).delete()
    db.commit()
    for c in q.choices:
        db_choice = Choices(choice_text=c.choice_text, is_correct=c.is_correct, question_id=db_question.id)
        db.add(db_choice)
        db.commit()
    
    return QuestionResponse(
        id=db_question.id,
        question_text=db_question.question_text,
        choices=[ChoiceBase(id=c.id, choice_text=c.choice_text, is_correct=c.is_correct) for c in db_question.choices]
    )
    
@router.delete("/questions/{q_id}/delete", response_model=SucessResponse)
async def delete_question_by_id(q_id: int, db: db_dependency, current_user: str = Depends(get_current_user)):
    db_question = db.query(Questions).filter(Questions.id==q_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    
    db.query(Choices).filter(Choices.question_id==db_question.id).delete()
    db.commit()
    db.delete(db_question)
    db.commit()
    
    return SucessResponse(message="Question deleted successfully!")

@router.delete("/questions/delete_all")
async def delete_all_questions(db: db_dependency, current_user: str = Depends(get_current_user)):
    try:
        db.query(Choices).delete()
        db.commit()

        db.query(Questions).delete()
        db.commit()

        return SucessResponse(message="All questions and choices have been deleted successfully.")
    except Exception as e:
        print(e)
        db.rollback() 
        raise HTTPException(status_code=500, detail="An error occurred while deleting questions.")
