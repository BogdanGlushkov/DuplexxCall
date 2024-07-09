from app.extensions import db
from datetime import datetime

class Users(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    PrefixName = db.Column(db.String(100), default=' ')


    def __repr__(self):
        return f'<User {self.name}>'
    
    def __init__(self, name):
        self.name = name
        
        
class Colors(db.Model):
    __tablename__ = "colors"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(7), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<Color {self.name} {self.code}>'
    
    def __init__(self, name, code):
        self.name = name
        self.code = code

class Metrics(db.Model):
    __tablename__ = "metrics"
    
    id = db.Column(db.Integer, primary_key=True)
    Data = db.Column(db.DateTime, nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    Operator = db.relationship("Users", backref=db.backref("metrics", lazy="dynamic"))
    StatusTimeInPlace = db.Column(db.Time)
    StatusTimeBusy = db.Column(db.Time)
    StatusTimeBreak = db.Column(db.Time)
    StatusTimeGone = db.Column(db.Time)
    StatusTimeNotAvailable = db.Column(db.Time)
    PercentInPlace = db.Column(db.Float)
    CountIncoming = db.Column(db.Integer)
    LenghtIncoming = db.Column(db.Time)
    IncomingAVG = db.Column(db.Time)
    CountOutgoing = db.Column(db.Integer)
    LenghtOutgoing = db.Column(db.Time)
    OutgoingAVG = db.Column(db.Time)
    CountMissed = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Metrics {self.Data}, {self.Operator}>'
    
    
class Schedule(db.Model):
    __tablename__ = "schedule"
    
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    Operator = db.relationship("Users", backref=db.backref("schedule", lazy="dynamic"))
    color_id = db.Column(db.Integer, db.ForeignKey('colors.id'), nullable=False, default=0)
    Color = db.relationship("Colors", backref=db.backref("schedule", lazy="dynamic"))
    data = db.Column(db.DateTime)
    startTime = db.Column(db.Time, nullable=False)
    endTime = db.Column(db.Time, nullable=False)
    
    isActive = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Schedule {self.id}>'