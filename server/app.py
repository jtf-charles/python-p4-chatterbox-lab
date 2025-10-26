from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages',methods=['GET','POST'])
def messages():
    if request.method=='GET':
        message_list=[]
        for message in Message.query.order_by(Message.created_at.asc()).all():
            message_serialized = message.to_dict()
            message_list.append(message_serialized)

        return make_response (message_list, 200  )
    
    elif request.method=='POST':
        payload = request.form
        if not payload:                              # si pas de form, tente JSON
            payload = request.get_json(silent=True) or {}

        body = (payload.get('body') or '').strip()
        username = (payload.get('username') or '').strip()

        # petites validations (évite les null côté front)
        if not body or not username:
            return make_response({'error': 'body and username are required'}, 400)

        m = Message(body=body, username=username)
        db.session.add(m)
        db.session.commit()
        db.session.refresh(m)  # pour récupérer created_at

        return make_response(m.to_dict(), 201)


@app.route("/messages/<int:id>", methods=["GET", "PATCH", "DELETE"])
def message_by_id(id):
    m = Message.query.filter(Message.id==id).first()

    if request.method == "GET":
        message_serialized = m.to_dict()
        return make_response(message_serialized, 200)

    if request.method == 'PATCH':
        # accepter form OU JSON
        data = request.form or (request.get_json(silent=True) or {})
        new_body = (data.get('body') or '').strip()
        if not new_body:
            return make_response({'error': 'body is required for PATCH'}, 400)

        m.body = new_body
        db.session.commit()
        return make_response(m.to_dict(), 200)

    db.session.delete(m)
    db.session.commit()
    return make_response({}, 204)
if __name__ == '__main__':
    app.run(port=5555)
