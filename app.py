from flask import Flask, render_template, redirect, request, url_for, session
from models import dbb #sqlAlchemy용
from models import User
from models import Question
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm, QuestionForm
import pymysql
app = Flask(__name__)

# pymysql을 사용해 DB 연결
db= pymysql.connect(host='localhost',
                     port=3306,
                     user='root',
                     passwd='password',
                     db='studyblank',
                     charset='utf8')

cursor = db.cursor()


@app.route('/')
def root():
    if 'user_email' in session: #세션 내에 email이 있는지 확인
        user_email = session.get('user_email', None)
        user_id = session.get('user_id', None)
        return render_template('home.html' , user_email = user_email, user_id=user_id)
    else:
        return render_template('home.html')


@app.route('/register', methods=['GET','POST'])
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

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        session['user_email'] = form.data.get('user_email')
        session['user_name'] = form.data.get('user_name')

        return redirect('/')

    return render_template('login.html',form=form)

@app.route('/logout',methods=['GET'])
def logout():
    session.clear()
    return redirect('/')


# 문제만들기 화면
@app.route('/question', methods=['GET','POST'])
def db_insert_q():
    form = QuestionForm()

    if form.validate_on_submit():
        question = Question()
        question.q_user_id = session['user_id']
        question.subject = form.data.get('subject')
        question.topic = form.data.get('topic')
        question.content = form.data.get('content')
        dbb.session.add(question)
        dbb.session.commit()
        return render_template('qeustion_success.html', name = session['user_email'] )
    return render_template('question_make.html', form = form, user_email= session['user_email'])






# 문제 보기

@app.route('/question/view')
@app.route('/question/view/<int:q_user_id>')
def view_question(q_user_id=None):
    if q_user_id ==None:
        sql = """SELECT * FROM question;"""
    else:
        sql = """SELECT * FROM question where q_user_id = {q_user_id};""".format(q_user_id=q_user_id)

    print(sql)
    cursor.execute(sql)
    result = cursor.fetchall()

    return render_template('question_list.html', result =result)




# 오답노트 보기

@app.route('/incorrect_note/view')
@app.route('/incorrect_note/view/<int:a_user_id>')
def view_incorrect_note(a_user_id = None, result = None):
    if a_user_id ==None:
        result= None
    else:
        sql = """SELECT a.user_answer, a.true_answer, q.content FROM answer a join question q on a.q_id =q.q_id where a_user_id = {a_user_id};""".format(a_user_id= a_user_id)

        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()

    return render_template('incorrect_list.html', a_user_id =a_user_id ,result = result)

@app.route('/incorrect_note', methods=['POST'])
def incorrect_note(a_user_id=None):
    if request.method =='POST':
        temp = request.form['a_user_id']
    else:
        temp =None
    return redirect(url_for('view_incorrect_note',a_user_id =temp))




# 문제 풀기
@app.route('/question/solve')
@app.route('/question/solve/<user>')
def solve_question(score=None, user =None):
    if user !=None:
        sql = """ SELECT q_id, content FROM question WHERE content IS NOT NULL AND q_user_id ={q_user_id}  ORDER BY RAND() LIMIT 10;""".format(q_user_id=user)

    else:
        sql = """ SELECT q_id, content FROM question WHERE content IS NOT NULL ORDER BY RAND() LIMIT 10;"""

    print(sql)
    cursor.execute(sql)
    result = cursor.fetchall()

    parsed = []

    answer_list=[]
    for i in result:
        parsed.append(parse_question(i))


    return render_template('question_solve.html',result =parsed ,answer_list = answer_list ,score = score)


# 문제 빈칸 파싱 함수
def parse_question(input):
    question = []  # 구멍 뚫린 문제를 만들기 위한 임시 리스트
    inputString = input[1]

    for i in range(len(inputString)):
        question.append(inputString[i])
    answersheet = list()  # 괄호안에 들어갈 정답

    for i in range(0, len(inputString)):
        if (inputString[i] == '('):
            temp = ''  # 정답 키워드를 빼내오기 위한 변수
            indexStart = i
            indexEnd = 0
            while (inputString[i] != ')'):
                i += 1
                if (inputString[i] != ')'):
                    temp += inputString[i]
                    indexEnd = i
            answersheet.append(temp)

            for j in range(indexStart + 1, indexEnd + 1):  # 괄호 안 키워드 대신 공백으로 채움
                question[j] = ' '
    return '/'.join(answersheet), ''.join(question), input[0]



# 성적 처리 및 오답노트db insert
@app.route('/grade', methods = ['POST'])
def grade(answer=None):
    if request.method == 'POST':
        user_answer = request.form.getlist('user_answer')
        real_answer = request.form.getlist('real_answer')
        real_question = request.form.getlist('real_question')
        q_id = request.form.getlist('q_id')
        grade_result =[]
        for i in range(len(user_answer)):
            print(user_answer[i], " ",real_answer[i])
            tmp=[]
            tmp.append(q_id[i])
            tmp.append(user_answer[i])
            tmp.append(real_answer[i])

            if user_answer[i] == real_answer[i]:
                tmp.append('정답')
            else:
                tmp.append('오답')
                sql = """INSERT INTO answer( a_user_id, user_answer, true_answer,q_id)
                         VALUES({a_user_id},\'{user_answer}\', \'{real_answer}\' , {q_id});"""
                sql = sql.format(a_user_id=session['user_id'],user_answer = user_answer[i], real_answer=real_answer[i], q_id=q_id[i])
                print(sql)
                cursor.execute(sql)
                db.commit()
            grade_result.append(tmp)

    else:
        answer = None



    return render_template('question_solve.html',real_answer=real_answer,real_question=real_question , score =grade_result )





if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/studyblank' ##서버의 db설정으로 변경 필요

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
    app.run()

