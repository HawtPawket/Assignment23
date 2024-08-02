from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:**YOURPASSWORD**@localhost/fitnesscenterdb'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Members(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)


class WorkOutSessions(db.Model):
    __tablename__ = 'workoutsessions'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False)
    session_date = db.Column(db.String(255), nullable=False)
    session_time = db.Column(db.String(320), nullable=False)
    activity = db.Column(db.String(15))
    


class MembersSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)
    class Meta:
        fields = ("id", "name", "age")

member_schema = MembersSchema()
members_schema = MembersSchema(many=True)


class WorkOutSessionsSchema(ma.Schema):
    id = fields.Integer(required=True)
    member_id = fields.Integer(required=True)
    session_date = fields.String(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)
    
    class Meta:
        fields = ("id", "member_id", "session_date", "session_time", "activity")

session_schema = WorkOutSessionsSchema()
sessions_schema = WorkOutSessionsSchema(many=True)

@app.route('/members', methods=['GET'])
def get_members():
    members = Members.query.all()
    return members_schema.jsonify(members)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_member = Members(id=member_data["id"], name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Members.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Members.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200



@app.route('/sessions', methods=['GET'])
def get_sessions():
    sessions = WorkOutSessions.query.all()
    return sessions_schema.jsonify(sessions)

@app.route('/sessions', methods=['POST'])
def add_session():
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_session = WorkOutSessions(id=session_data["id"], member_id=session_data['member_id'], session_date=session_data['session_date'], session_time=session_data['session_time'], activity=session_data['activity'], trainer_id=session_data['trainer_id'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"message": "New Session added successfully"}), 201

@app.route('/sessions/<int:id>', methods=['PUT'])
def update_session(id):
    session = WorkOutSessions.query.get_or_404(id)
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    session.member_id = session_data['member_id']
    session.session_date = session_data['session_date']
    session.session_time = session_data['session_time']
    session.activity = session_data['activity']
    
    db.session.commit()
    return jsonify({"message": "Session detail updated successfully"}), 200

@app.route('/sessions/<int:id>', methods=['DELETE'])
def delete_session(id):
    session = WorkOutSessions.query.get_or_404(id)
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "Session removed successfully"}), 200


@app.route('/members/<int:member_id>/sessions', methods=['GET'])
def get_sessions_by_member(member_id):
    sessions = WorkOutSessions.query.filter_by(member_id=member_id).all()
    return sessions_schema.jsonify(sessions)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)