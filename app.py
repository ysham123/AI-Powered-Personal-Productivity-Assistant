from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoid warnings

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define Task model
class Task(db.Model):
    id = db.Column('task_id', db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    priority = db.Column(db.String(50))
    status = db.Column(db.String(10))

    def __init__(self, title, description, priority, status):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status

# Define routes
@app.route("/")  # Homepage route
def home():
    return "Hello, Flask!"

@app.route("/task_page", methods=["GET"])  # Tasks route placeholder
def task_page():
    return {"tasks": []}  # Placeholder: Return empty task list

@app.route("/tasks", methods = ["POST"])
def handle_post():
    data = request.get_json() #parsing the json from the request
    
    #valid the requried fields
    if not all(key in data for key in ("title", "priority", "status")):
        return jsonify({"error": "Missing required fields"}), 400 #returning 400 if validation fails
    
    #create a new task object
    new_task = Task(
        title = data["title"],
        description=data.get("description", ""), #optional field
        priority=data["priority"],
        status=data["status"]
    )

    #adding the new task to the data base

    db.session.add(new_task)
    db.session.commit()

    #return a success response

    return jsonify({"message": "Task added successfully!"}), 201

# Run the app
if __name__ == "__main__":
    # Create database tables before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True)
