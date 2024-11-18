from typing import List
from pydantic import BaseModel


class ChoiceBase(BaseModel):
    id: int | None=None
    choice_text: str
    is_correct: bool

class QuestionBase(BaseModel):
    id: int | None=None
    question_text: str
    choices: List[ChoiceBase]

class QuestionResponse(BaseModel): 
    id: int | None=None
    question_text: str
    choices: List[ChoiceBase]
    
class SucessResponse(BaseModel):
    message: str