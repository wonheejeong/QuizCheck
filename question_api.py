from flask import Blueprint
from flask import Flask, render_template, redirect, request, url_for, session
from models import dbb #sqlAlchemy용
from models import User
from models import Question
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm, QuestionForm
import pymysql

question_api = Blueprint('question_api', __name__)

# pymysql을 사용해 DB 연결
db= pymysql.connect(host='localhost',
                     port=3306,
                     user='test',
                     passwd='passwd',
                     db='studyblank',
                     charset='utf8')


cursor = db.cursor()


# 문제만들기
@question_api.route('/question', methods=['GET','POST'])
def db_insert_q():
    if 'user_id' and 'user_email' not in session:
        return redirect('/')
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

@question_api.route('/question/view')
@question_api.route('/question/view/<int:q_user_id>')
def view_question(q_user_id=None):
    if 'user_id' and 'user_email' not in session:
        return redirect('/')
    if q_user_id ==None:
        sql = """SELECT * FROM question;"""
    else:
        sql = """SELECT * FROM question where q_user_id = {q_user_id};""".format(q_user_id=q_user_id)

    print(sql)
    cursor.execute(sql)
    result = cursor.fetchall()

    return render_template('question_list.html', result =result, user_id= session['user_id'])




# 오답노트 보기

@question_api.route('/incorrect_note/view')
def view_incorrect_note():
    if 'user_id' and 'user_email' not in session:
        return redirect('/')
    user_id = session['user_id']
    if user_id ==None:
        result= None
    else:
        sql = """SELECT a.user_answer, a.true_answer, q.content FROM answer a join question q on a.q_id =q.q_id where a_user_id = {a_user_id};""".format(a_user_id= user_id)

        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()

    return render_template('incorrect_list.html', user_id =user_id ,user_email = session['user_email'],result = result)

@question_api.route('/incorrect_note', methods=['POST'])
def incorrect_note(a_user_id=None):
    if request.method =='POST':
        temp = request.form['a_user_id']
    else:
        temp =None
    return redirect(url_for('view_incorrect_note',a_user_id =temp))




# 문제 풀기
@question_api.route('/question/solve')
@question_api.route('/question/solve/<int:user>')
def solve_question(score=None, user =None):
    if 'user_id' and 'user_email' not in session:
        return redirect('/')
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


    return render_template('question_solve.html',result =parsed ,answer_list = answer_list ,score = score, user_id =session['user_id'])


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



# 성적 처리 및 오답노트 생성
@question_api.route('/grade', methods = ['POST'])
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

