from flask_wtf import FlaskForm
from models import User
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from flask import session
from models import dbb

class RegisterForm(FlaskForm):
    #이메일과 이름 중복 체크를 하는 코드
    class DuplicateEmailCheck(object):
        def __init__(self, message=None):
            self.message = message
        def __call__(self,form, field):
            #user_email = form['user_email'].data
            user_email = field.data
            samemail = User.query.filter_by(user_email=user_email).first()
            if samemail:
                raise ValueError('  !이미 존재하는 이메일입니다.')

    class DuplicateNameCheck(object):
        def __init__(self, message=None):
            self.message = message
        def __call__(self,form, field):
            #user_name = form['user_name'].data
            user_name = field.data
            samename = User.query.filter_by(user_name=user_name).first()
            if samename:
                raise ValueError('  !이미 존재하는 닉네임입니다.')
    user_email = StringField('user_email', validators=[DataRequired(), DuplicateEmailCheck()])
    user_name = StringField('user_name', validators=[DataRequired(), DuplicateNameCheck()])
    user_pw = PasswordField('user_pw', validators=[DataRequired(), EqualTo('re_password')])
    re_password = PasswordField('re_password', validators=[DataRequired()])


class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message
        def __call__(self,form,field):
            user_email = form['user_email'].data
            user_pw = field.data
            user = User.query.filter_by(user_email=user_email).first()
            if user !=None:
                if  user.user_pw != user_pw:
                    raise ValueError('  잘못된 아이디나 비밀번호입니다.')
                else:
                    session['user_email'] = user_email
                    for_id = dbb.session.query(User.user_id).filter(User.user_email == session['user_email']).all()
                    user_id = ''
                    for what in for_id:
                        user_id = what[0]
                    session['user_id'] = user_id
            else:
                raise ValueError('  잘못된 아이디나 비밀번호입니다.')

    user_email = StringField('user_email', validators=[DataRequired()])
    user_pw = PasswordField('user_pw', validators=[DataRequired(), UserPassword()])


class QuestionForm(FlaskForm):
    subject = StringField('subject',validators=[DataRequired()])
    topic = StringField('topic',validators=[DataRequired()])
    content = StringField('content',validators=[DataRequired()])