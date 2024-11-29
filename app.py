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

@app.route("/tasks", methods = ["GET"])
def retrieve_tasks():
    #fetch all the tasks from the database
    tasks = Task.query.all()

    #convert the tasks into dictionaries
    task_list = []
    for task in tasks:
        task_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status
        })
    #return the JSON response
    return jsonify(task_list)

@app.route("/tasks/<int:id?", methods = ["PUT,"])

def update_task(id):
    #fetch the id
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "task doesnt exist"}), 404
    
    #get the required data
    data = request.get_json()

    #update the fields if they exist
    updatable_fields = ["title", "description", "priority", "status"]

    #update the fields dynamically
    for field in updatable_fields:
        if field in data:
            setattr(task, field, data[field]) #dynamically set the attribute
    
    #commit the changes to the database
    db.session.commit()

    #return the success response with the updated task
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status
    }), 200


# Run the app
if __name__ == "__main__":
    # Create database tables before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True)
