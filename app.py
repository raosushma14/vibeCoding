from flask import Flask, request, jsonify
from models import db, TeamMember, Task
from datetime import datetime, date, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vibe_coding.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Seed Data
def seed_data():
    # Create 5 team members
    team_members = [
        TeamMember(name="Alice"),
        TeamMember(name="Bob"),
        TeamMember(name="Charlie"),
        TeamMember(name="Diana"),
        TeamMember(name="Eve")
    ]
    db.session.bulk_save_objects(team_members)
    db.session.commit()

    # Query the team members from the database to get their IDs
    team_members = TeamMember.query.all()

    # Get yesterday's date
    yesterday = datetime.utcnow() - timedelta(days=1)

    # Create 10 tasks assigned to the team members
    tasks = [
        Task(title=f"Task {i+1}", assigned_to=team_members[i % 5].id, date_assigned=yesterday, status="Pending", impediments="No Impediments")
        for i in range(10)
    ]
    db.session.bulk_save_objects(tasks)
    db.session.commit()

    print("Seed data added successfully!")

# Initialize database and seed data
with app.app_context():
    db.create_all()
    seed_data()

# Add a team member
@app.route('/add_member', methods=['POST'])
def add_member():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    new_member = TeamMember(name=name)
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Team member added successfully', 'team_member': {'id': new_member.id, 'name': new_member.name}}), 201

# Assign a task
@app.route('/assign_task', methods=['POST'])
def assign_task():
    data = request.json
    title = data.get('title')
    assigned_to = data.get('assigned_to')
    if not title or not assigned_to:
        return jsonify({'error': 'Title and assigned_to are required'}), 400
    member = TeamMember.query.filter_by(name=assigned_to).first()
    if not member:
        return jsonify({'error': 'Assigned member does not exist'}), 404
    new_task = Task(title=title, assigned_to=member.id, date_assigned=datetime.utcnow())
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task assigned successfully', 'task': {'id': new_task.id, 'title': new_task.title, 'assigned_to': member.name, 'status': new_task.status}}), 201

# Update task status
@app.route('/update_task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    status = data.get('status')
    impediments = data.get('impediments')
    if not status:
        return jsonify({'error': 'Status is required'}), 400
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    task.status = status
    if status == 'Completed':
        task.percent_complete = 100.0
    elif status == 'In Progress':
        task.percent_complete = 50.0
    else:
        task.percent_complete = 0.0
    if impediments:
        task.impediments = impediments
    db.session.commit()
    return jsonify({'message': 'Task status updated successfully', 'task': {'id': task.id, 'title': task.title, 'status': task.status, 'impediments': task.impediments}}), 200

# Get today's task summary
@app.route('/tasks/summary', methods=['GET'])
def get_todays_task_summary():
    today = date.today()
    tasks = Task.query.filter(Task.date_assigned >= datetime(today.year, today.month, today.day)).all()
    task_summary = [{'id': task.id, 'title': task.title, 'assigned_to': task.assigned_member.name, 'status': task.status} for task in tasks]
    return jsonify({'tasks': task_summary}), 200

# Get impediments
@app.route('/tasks/impediments', methods=['GET'])
def get_impediments():
    tasks_with_impediments = Task.query.filter(Task.impediments.isnot(None)).all()
    impediments = [{'id': task.id, 'title': task.title, 'impediments': task.impediments} for task in tasks_with_impediments]
    return jsonify({'impediments': impediments}), 200

# Fetch all tasks and team members
@app.route('/all_data', methods=['GET'])
def fetch_all_data():
    # Fetch all team members
    team_members = TeamMember.query.all()
    team_members_data = [{'id': member.id, 'name': member.name} for member in team_members]

    # Fetch all tasks
    tasks = Task.query.all()
    tasks_data = [
        {
            'id': task.id,
            'title': task.title,
            'assigned_to': task.assigned_member.name,
            'status': task.status,
            'percent_complete': task.percent_complete,
            'impediments': task.impediments,
            'date_assigned': task.date_assigned.strftime('%Y-%m-%d %H:%M:%S')
        }
        for task in tasks
    ]

    return jsonify({'team_members': team_members_data, 'tasks': tasks_data}), 200

if __name__ == '__main__':
    app.run(debug=True)