from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<TeamMember id={self.id} name={self.name}>"

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('team_members.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    percent_complete = db.Column(db.Float, nullable=False, default=0.0)
    impediments = db.Column(db.String(500), nullable=True)
    date_assigned = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    assigned_member = db.relationship('TeamMember', backref='tasks')

    def __repr__(self):
        return (f"<Task id={self.id} title={self.title} assigned_to={self.assigned_to} "
                f"status={self.status} percent_complete={self.percent_complete}>")