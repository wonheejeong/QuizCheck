from flask_wtf import FlaskForm
from models import User
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo

class RegisterForm(FlaskForm):
    user_email = StringField('user_email', validators=[DataRequired()])
    user_name = StringField('user_name', validators=[DataRequired()])
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
            if user.user_pw != user_pw:
                # raise ValidationError(message % d)
                raise ValueError('Wrong user_pw')
    user_email = StringField('user_email', validators=[DataRequired()])
    user_pw = PasswordField('user_pw', validators=[DataRequired(), UserPassword()])

class QuestionForm(FlaskForm):
    subject = StringField('subject',validators=[DataRequired()])
    topic = StringField('topic',validators=[DataRequired()])
    content = StringField('content',validators=[DataRequired()])