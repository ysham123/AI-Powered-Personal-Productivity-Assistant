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
    id = db.Column(db.Integer, primary_key=True)  # Corrected column definition
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    priority = db.Column(db.String(50))
    status = db.Column(db.String(10))

    def __init__(self, title, description, priority, status):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status

# Routes
@app.route("/")  # Homepage route
def home():
    return "Hello, Flask!"

@app.route("/tasks", methods=["POST"])
def handle_post():
    data = request.get_json()  # Parsing the JSON from the request
    
    # Validate required fields
    if not all(key in data for key in ("title", "priority", "status")):
        return jsonify({"error": "Missing required fields"}), 400  # Return 400 if validation fails
    
    # Create a new task object
    new_task = Task(
        title=data["title"],
        description=data.get("description", ""),  # Optional field
        priority=data["priority"],
        status=data["status"]
    )

    # Add the new task to the database
    db.session.add(new_task)
    db.session.commit()

    # Return a success response
    return jsonify({"message": "Task added successfully!"}), 201

@app.route("/tasks", methods=["GET"])
def retrieve_tasks():
    # Fetch all the tasks from the database
    tasks = Task.query.all()

    # Convert tasks to dictionaries using a list comprehension
    task_list = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status
        }
        for task in tasks
    ]

    # Return the JSON response
    return jsonify(task_list)

@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    # Fetch the task by ID
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task doesn't exist"}), 404
    
    # Get the updated data
    data = request.get_json()

    # Update the fields dynamically
    updatable_fields = ["title", "description", "priority", "status"]
    for field in updatable_fields:
        if field in data:
            setattr(task, field, data[field])  # Dynamically set the attribute
    
    # Commit changes to the database
    db.session.commit()

    # Return a success response with the updated task
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status
    }), 200

@app.route("/tasks/<int:id>", methods = ["Delete"])

def delete_task(id):
    #fetching the task by the id
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    #Delete the task from the database
    db.session.delete(task)
    db.session.commit()

    #return the success response
    return jsonify({"message": "Task deleted successfully"}), 200

# Run the app
if __name__ == "__main__":
    with app.app_context():
        print("Attempting to create database...")
        db.create_all()
        print("Database creation complete!")
    app.run(debug=True)
