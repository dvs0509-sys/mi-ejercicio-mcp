"""
Database configuration and models for Mergington High School API
"""

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pathlib import Path
from datetime import datetime

# Database setup - store in src directory
DB_PATH = Path(__file__).parent / "mergington.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Association table for many-to-many relationship between activities and participants
activity_participants = Table(
    'activity_participants',
    Base.metadata,
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True),
    Column('participant_email', String, ForeignKey('participants.email'), primary_key=True),
    Column('signup_date', DateTime, default=datetime.utcnow)
)


class Activity(Base):
    """Activity model"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    schedule = Column(String)
    max_participants = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to participants
    participants = relationship(
        "Participant",
        secondary=activity_participants,
        back_populates="activities"
    )

    def to_dict(self):
        """Convert activity to dictionary format"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": [p.email for p in self.participants],
            "current_participants": len(self.participants)
        }


class Participant(Base):
    """Participant model"""
    __tablename__ = "participants"

    email = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to activities
    activities = relationship(
        "Activity",
        secondary=activity_participants,
        back_populates="participants"
    )

    def to_dict(self):
        """Convert participant to dictionary format"""
        return {
            "email": self.email,
            "activities": [a.name for a in self.activities],
            "created_at": self.created_at.isoformat()
        }


def init_db():
    """Initialize database with schema and seed data"""
    Base.metadata.create_all(bind=engine)
    
    # Check if data already exists
    db = SessionLocal()
    try:
        existing_activities = db.query(Activity).count()
        if existing_activities == 0:
            # Seed initial data
            seed_initial_data(db)
    finally:
        db.close()


def seed_initial_data(db):
    """Seed database with initial activity data"""
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and play basketball with the school team",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore your creativity through painting and drawing",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and produce plays and performances",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
        },
        "Math Club": {
            "description": "Solve challenging problems and participate in math competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
        }
    }

    for activity_name, activity_data in initial_activities.items():
        # Create activity
        activity = Activity(
            name=activity_name,
            description=activity_data["description"],
            schedule=activity_data["schedule"],
            max_participants=activity_data["max_participants"]
        )

        # Create/get participants and add to activity
        for email in activity_data["participants"]:
            participant = db.query(Participant).filter(Participant.email == email).first()
            if not participant:
                participant = Participant(email=email)
                db.add(participant)
            activity.participants.append(participant)

        db.add(activity)

    db.commit()


def get_db():
    """Dependency for getting database session in FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
