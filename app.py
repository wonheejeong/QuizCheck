from flask import Flask, render_template, redirect, request, url_for, session
from login_api import login_api
from question_api import question_api
from models import dbb #sqlAlchemy용
from models import User
from models import Question
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm, QuestionForm
import pymysql


app = Flask(__name__)

app.register_blueprint(login_api)
app.register_blueprint(question_api)




if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://test:passwd@localhost/studyblank' ##서버의 db설정으로 변경 필요

    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'

    #csrf 위변조 공격을 막기위한 코드
    csrf = CSRFProtect()
    CSRFProtect(app)
    csrf.init_app(app)

    dbb.init_app(app)
    dbb.app = app
    dbb.create_all()  # SQLAlchemy 이용한 db 생성
    app.run(host='127.0.0.1', port=5000)
