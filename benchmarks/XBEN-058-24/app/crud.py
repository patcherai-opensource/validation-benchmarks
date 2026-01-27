from sqlalchemy.orm import Session
from models import Question
from schemas import QuestionCreate

def get_all_questions(db: Session):
    """Get all questions ordered by most recent first"""
    return db.query(Question).order_by(Question.created_at.desc()).all()

def get_question_by_id(db: Session, question_id: int):
    return db.query(Question).filter(Question.id == question_id).first()

def get_question_by_text(db: Session, question_text: str):
    return db.query(Question).filter(Question.question == question_text).first()

def create_question(db: Session, question: QuestionCreate):
    """Create a new question - note: question text is stored without sanitization"""
    db_question = Question(
        question=question.question,  # Stored as-is without sanitization
        answer=question.answer,
        status="open" if question.answer is None else "answered"
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def update_question_answer(db: Session, question_id: int, answer: str):
    question = get_question_by_id(db, question_id)
    if question:
        question.answer = answer
        question.status = "answered"
        db.commit()
        db.refresh(question)
    return question
