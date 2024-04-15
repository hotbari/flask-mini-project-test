from flask import Flask
from flask_migrate import Migrate
import os
from .database import db
from datetime import datetime, timedelta
from .models import Participant, Admin, Question, Quiz
from werkzeug.security import generate_password_hash
import click
from flask.cli import with_appcontext


# Flask 애플리케이션을 생성하고 설정하며 데이터베이스 초기화 명령을 추가하는 함수
def create_app():
    app = Flask(__name__)
    app.secret_key = "oz_coding_secret"

    # 데이터베이스 파일 경로 설정 및 앱 설정
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    dbfile = os.path.join(basedir, "db.sqlite")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + dbfile
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 데이터베이스 및 마이그레이션 초기화
    db.init_app(app)
    migrate = Migrate(app, db)

    # 라우트(블루프린트) 등록
    from .routes import main as main_blueprint
    from .routes import admin as admin_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)


    # 초기화 명령어
    def add_initial_questions():
        initial_questions = [
            "5일안에 미니 프로젝트를 완성",
            "프로그래밍 언어 1개 마스터",
            "매일 운동",
            "잠들기 전 스마트폰 하지 않기"
        ]

        # 어제 날짜
        yesterday = datetime.utcnow() - timedelta(days=1)

        # 어드민 계정 추가, 비밀번호 해쉬
        existing_admin = Admin.query.filter_by(username="admin").first()
        if not existing_admin:
            hashed_password= generate_password_hash("1234")
            new_admin = Admin(username="admin", password=hashed_password)
            db.session.add(new_admin)

        # 생성 날짜가 없는 참가자
        participants_without_created_at = Participant.query.filter(Participant.created_at==None).all()

        for participant in participants_without_created_at:
            participant.created_at = yesterday


        # 기본 질문 외의 질문컨텐츠 추가
        for question_content in initial_questions:
            existing_question = Question.query.filter_by(content=question_content).first()
            if not existing_question:
                new_question = Question(content=question_content)
                db.session.add(new_question)
            
            questions = Question.query.all()

        # 모든 질문을 활성화
        for question in questions:
            question.order_num = question.id
            question.is_active = True

        db.session.commit()

    # Python에서 Flask 애플리케이션을 설정하고 데이터베이스 초기화를 위한 명령을 추가하는 부분 
    # Flask의 확장인 Click을 사용하여 명령 라인 인터페이스(Command Line Interface, CLI)를 구축

    # Click에서 init-db라는 명령을 정의. 
    # 이 명령은 데이터베이스를 초기화하는 역할을 할 것으로 예상
    @click.command("init-db")

    # 이 데코레이터는 Flask 애플리케이션 컨텍스트 내에서 함수를 실행하도록 보장
    # Flask 애플리케이션 컨텍스트를 설정하지 않으면 Flask 환경에서 작업을 수행할 수 없다
    @with_appcontext

    # 데이터베이스를 생성하고 초기 질문을 추가한 후 메시지를 출력
    def init_ab_command():
        db.create_all()
        add_initial_questions()
        click.echo("Initialized the DB")

    # Flask 애플리케이션에 init_ab_command 함수를 명령으로 추가
    # 이렇게 하면 Flask 애플리케이션을 실행할 때 flask init-db 명령을 사용하여 데이터베이스를 초기화할 수 있습니다.
    app.cli.add_command(init_ab_command)

        

    return app