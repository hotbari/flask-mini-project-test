from flask import Blueprint, Flask, render_template, request, jsonify
from .database import db
from waitress import serve
from .models import Participant, Answer

main = Blueprint("main", __name__)


@main.route('/', methods=['GET'] )
def index():
    return render_template('index.html')

@main.route('/participant', methods=["POST"])
def add_participant():
    data = request.get_json()
    new_participant = Participant(
        name=data["name"],
    )
    db.session.add(new_participant)
    db.session.commit()

    return jsonify({"redirect":"/questions", "participant_id":new_participant.id})


@main.route('/questions', methods=['POST', 'GET'])
def question():
    return render_template('questions.html')



@main.route('/result')
def res_result():
    return render_template('esult.html')
