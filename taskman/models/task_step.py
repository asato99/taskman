"""
TaskStep model implementation
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from taskman.models.base import BaseModel

class TaskStep(BaseModel):
    """
    TaskStep model representing a step in a task
    """
    __tablename__ = 'task_step'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    step_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    expected_duration = Column(Integer)  # in minutes
    required_resources = Column(Text)
    verification_method = Column(Text)

    # Relationships
    task = relationship('Task', back_populates='steps') 