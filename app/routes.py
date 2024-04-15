from flask import (jsonify, render_template, request, Blueprint, redirect, url_for, flash, session, )
from .database import db
from .models import Participant, Question, Quiz, Admin
from werkzeug.security import check_password_hash
import json
from sqlalchemy import func, extract
from datetime import datetime

# 시각화
import plotly.express as px
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.offline import plot


# 라우트를 크게 두 개로 쪼개쪼개용용
main = Blueprint("main", __name__)
admin = Blueprint("admin", __name__, url_prefix="/admin/")


# main

@main.route('/', methods=['GET'] )
def home():
    return render_template('index.html')


@main.route('/participants', methods=["POST"])
def add_participant():
    data = request.get_json()
    new_participant = Participant(
        name=data["name"],
        created_at=datetime.utcnow()
    )
    db.session.add(new_participant)
    db.session.commit()

    return jsonify({"redirect":url_for("main.quiz"), "participant_id":new_participant.id})


@main.route('/quiz')
def quiz():
    participant_id = request.cookies.get("participant_id")
    if not participant_id:
        return redirect(url_for("main.home"))
    
    questions = Question.query.all()
    questions_list = [question.content for question in questions]
    return render_template("quiz.html", questions=questions_list)


@main.route('/submit', methods=['POST'])
def submit():
    participant_id = request.cookies.get("participant_id")
    if not participant_id:
        return jsonify({"error":"Participant ID not found"}), 400
    
    data = request.json
    quizzes = data.get("quizzes", [])

    for quiz in quizzes:
        question_id = quiz.get("question_id")
        chosen_answer = quiz.get("chosen_answer")

        new_quiz_entry = Quiz(
            participant_id = participant_id,
            question_id = question_id,
            chosen_answer = chosen_answer
        )

        db.session.add(new_quiz_entry)

    db.session.commit()
    return jsonify(
        {
            "msg":"Quiz answers submitted successfully",
            "redirect": url_for("main.show_results")
        }
    )


@main.route('/questions')
def get_questions():
    questions = (
        Question.query.filter(Question.is_active == True).order_by(Question.order_num).all()
    )
    question_list = [
        {
            "id": question.id,
            "content": question.content,
            "order_num": question.order_num,
        }
        for question in questions
    ]
    return jsonify(questions=question_list)


@main.route('/results')
def show_results():
    # db 조회
    participant_query = Participant.query.all()
    quizzes_query = Quiz.query.join(Question).all()

    '''
    가능을 누른만큼 possible percent 출력
    (가능 선택한 질문 개수 / 전체 질문 갯수 * 100) % 로 가능도 출력 (.2f)
    전체 00명 중 0등 출력

    전체 데이터를 조회해서 df로 변환, 가능도가 높은 순으로 정렬
    전체 인덱스에서 특정 참가자의 데이터의 인덱스+1
    당신의 가능 등수는 {전체 인덱스} 중 {참가자의 인덱스+1}등 입니다!
    '''


# admin

@admin.route('/', methods=["GET"," POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):
            session["admin_logged_in"]=True
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid username or password")

    # POST가 아니면       
    return render_template("admin.html")


@admin.route('/logout')
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.login"))


from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session:
            return redirect(url_for("admin.login", next=request.url)) # 로그인하고 이전 페이지로 리다이렉트
        return f(*args, **kwargs)
    
    return decorated_function


@admin.route('dashboard')
@login_required
def dashboard():
    participant_counts = {
        db.session.query(
            func.date(Participant.created_at).label("date"),
            func.count(Participant.id).label("count")
        ).group_by("date").all()
    }

    dates = [result.date for result in participant_counts]
    counts = [result.count for result in participant_counts]

    graph = go.Figure(go.Scatter(x=dates, y=counts, mode="lines+markers"))

    graph.update_layout(title="일자별 참가자 수", xaxis_title="날짜", yaxis_title="참가자 수")

    # 그래프 html로 변환
    graph_div = plot(graph, output_type="div", include_plotlyjs=False, config= {'displayModeBar': False})

    return render_template("dashboard.html", graph_div=graph_div)


@admin.route('/dashboard/question', methods=['GET','POST'])
@login_required
def manage_questions():
    pass
