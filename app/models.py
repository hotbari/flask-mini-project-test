from .database import db
import pytz
from datetime import datetime

class Participant(db.Model):
    __tablename__ = "participant"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    created_date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone("Asia/Seoul")))

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer)
    chosen_answer = db.Column(db.Integer)
    participant_id = db.Column(db.Integer, db.ForeignKey("participant.id"))
    participant = db.relationship("Participant", backref="answers")