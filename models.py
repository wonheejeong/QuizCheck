#DB
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

dbb = SQLAlchemy()

class User(dbb.Model):
    __tablename__='user'
    user_id = dbb.Column(dbb.Integer, primary_key = True, unique=True, autoincrement=True)
    user_name = dbb.Column(dbb.String(100))
    user_email = dbb.Column(dbb.String(100))  # 이메일 == ID
    user_pw = dbb.Column(dbb.String(100))


class Question(dbb.Model):
    __tablename__ = 'question'
    q_id = dbb.Column(dbb.Integer,primary_key = True, unique=True, autoincrement=True)
    q_user_id = dbb.Column(dbb.Integer, ForeignKey('user.user_id'))
    subject = dbb.Column(dbb.String(255))
    topic = dbb.Column(dbb.String(255))
    content = dbb.Column(dbb.String(1000))
class Answer(dbb.Model):
    __tablename__ = 'answer'
    a_id = dbb.Column(dbb.Integer, primary_key=True, unique=True, autoincrement=True)
    a_user_id = dbb.Column(dbb.Integer, ForeignKey('user.user_id'))
    user_answer = dbb.Column(dbb.String(255))
    true_answer = dbb.Column(dbb.String(255))
    chk = dbb.Column(dbb.Integer)
    q_id = dbb.Column(dbb.Integer,ForeignKey('question_q_id'))
    blank = dbb.Column(dbb.String(1000))