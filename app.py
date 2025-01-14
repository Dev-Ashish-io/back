from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from models import db, Team, Transaction

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Route to get all teams
@app.route('/teams', methods=['GET'])
def get_teams():
    """Fetch all teams and their details"""
    teams = Team.query.all()
    return jsonify([team.to_dict() for team in teams])

# Route to add a transaction
@app.route('/transactions', methods=['POST'])
def add_transaction():
    """Record a buy/sell transaction"""
    data = request.json
    try:
        new_transaction = Transaction(
            team_id=data['team_id'],
            stock_name=data['stock_name'],
            quantity=data['quantity'],
            price=data['price'],
            action=data['action']
        )
        db.session.add(new_transaction)
        db.session.commit()

        # Update team stocks and money
        team = Team.query.get(data['team_id'])
        team.update_stock(data['stock_name'], data['quantity'], data['price'], data['action'])
        db.session.commit()

        # Send live updates via WebSocket
        teams = Team.query.all()
        socketio.emit('update', {'teams': [team.to_dict() for team in teams]})
        return jsonify({'message': 'Transaction added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# New route to handle transactions (GET & POST)
@app.route("/api/transactions", methods=["GET", "POST"])
def handle_transactions():
    if request.method == "GET":
        try:
            # Replace with actual database logic if needed
            transactions = [{"id": 1, "name": "Transaction 1", "amount": 1000}]
            return jsonify(transactions)
        except Exception as e:
            return jsonify({'error': f"Failed to fetch transactions: {str(e)}"}), 500
    
    if request.method == "POST":
        try:
            new_transaction = request.get_json()
            # Here you can add the logic to save the transaction to the database
            return jsonify({"message": "Transaction added successfully!"}), 201
        except Exception as e:
            return jsonify({"error": f"Failed to add transaction: {str(e)}"}), 500

# WebSocket connection event
@socketio.on('connect')
def handle_connect():
    print('A client connected.')

# Index route (optional, can be customized)
@app.route("/")
def index():
    return "Hello, Flask with SocketIO!"

# Run the app with SocketIO
if __name__ == '__main__':
    from app import socketio
    socketio.run(app, host='0.0.0.0', port=10000)

