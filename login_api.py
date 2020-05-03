from flask import Blueprint
from flask import Flask, render_template, redirect, request, url_for, session
from models import dbb #sqlAlchemy용
from models import User
from models import Question
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm, QuestionForm


login_api = Blueprint('login_api', __name__)


@login_api.route('/')
def root():
    if 'user_email' in session: #세션 내에 email이 있는지 확인
        user_email = session.get('user_email', None)
        user_id = session.get('user_id', None)
        return render_template('home.html' , user_email = user_email, user_id=user_id)
    else:
        return render_template('home.html')


@login_api.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.user_email = form.data.get('user_email')
        user.user_name = form.data.get('user_name')
        user.user_pw = form.data.get('user_pw')

        print(user.user_email, user.user_pw) #콘솔 확인용

        dbb.session.add(user)
        dbb.session.commit()

        return redirect('/login')
    return render_template('register.html',form=form)

@login_api.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        session['user_email'] = form.data.get('user_email')
        session['user_name'] = form.data.get('user_name')

        return redirect('/')

    return render_template('login.html',form=form)

@login_api.route('/logout',methods=['GET'])
def logout():
    session.clear()
    return redirect('/')