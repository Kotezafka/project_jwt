from flask import Flask, request, jsonify
from flask.cli import load_dotenv
import jwt
import os
from models import db, Message

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
db.init_app(app)


@app.route('/messages', methods=['POST'])
def create_message():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is missing or invalid'}), 400

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 400

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    message = data.get('message')
    if not message or not message.strip():
        return jsonify({'error': 'Message cannot be empty'}), 400

    new_message = Message(
        user_id=payload['user_id'],
        message=message.strip()
    )
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'message': 'Message created successfully', 'id': new_message.id}), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001)
