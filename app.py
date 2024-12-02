from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate, ValidationError

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoid warnings

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    priority = db.Column(db.String(50))
    status = db.Column(db.String(10))

    def __init__(self, title, description, priority, status):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status

# Define Marshmallow schema for validation
class TaskSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(validate=validate.Length(max=200))
    priority = fields.String(required=True, validate=validate.OneOf(["High", "Medium", "Low"]))
    status = fields.String(required=True, validate=validate.OneOf(["Pending", "Completed"]))

# Instantiate the schema
task_schema = TaskSchema()

# Routes
@app.route("/")  # Homepage route
def home():
    return "Hello, Flask!"

@app.route("/tasks", methods=["POST"])
def handle_post():
    data = request.get_json()

    # Validate input using Marshmallow schema
    try:
        validated_data = task_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Create a new task object
    new_task = Task(
        title=validated_data["title"],
        description=validated_data.get("description", ""),  # Optional field
        priority=validated_data["priority"],
        status=validated_data["status"]
    )

    # Add the new task to the database
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task added successfully!"}), 201

@app.route("/tasks", methods=["GET"])
def retrieve_tasks():
    # Step 1: Extract query parameters for filtering and pagination
    priority = request.args.get('priority')
    status = request.args.get('status')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=5, type=int)

    # Step 2: Build the base query
    query = Task.query

    # Step 3: Dynamically add filters
    if priority:
        query = query.filter(Task.priority == priority)
    if status:
        query = query.filter(Task.status == status)

    # Step 4: Apply pagination
    paginated_tasks = query.paginate(page=page, per_page=per_page, error_out=False)

    # Step 5: Convert tasks to dictionaries
    tasks = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status
        }
        for task in paginated_tasks.items
    ]

    # Step 6: Return tasks with pagination metadata
    return jsonify({
        "tasks": tasks,
        "meta": {
            "total_items": paginated_tasks.total,
            "total_pages": paginated_tasks.pages,
            "current_page": paginated_tasks.page,
            "per_page": paginated_tasks.per_page
        }
    })

@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task doesn't exist"}), 404

    data = request.get_json()

    # Validate input using Marshmallow schema
    try:
        validated_data = task_schema.load(data, partial=True)  # Allow partial updates
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Update the task dynamically
    for key, value in validated_data.items():
        setattr(task, key, value)

    db.session.commit()

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status
    }), 200

@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200

# Run the app
if __name__ == "__main__":
    with app.app_context():
        print("Attempting to create database...")
        db.create_all()
        print("Database creation complete!")
    app.run(debug=True)
