"""
Task model implementation
"""
from sqlalchemy import Column, String, Text, Integer, Enum, ForeignKey, Date
from sqlalchemy.orm import relationship

from taskman.models.base import BaseModel

class Task(BaseModel):
    """
    Task model representing a work item
    """
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    estimated_duration = Column(Integer)  # in minutes
    status = Column(
        Enum('未着手', '進行中', '完了', '保留', name='task_status'),
        default='未着手'
    )
    priority = Column(
        Enum('低', '中', '高', '緊急', name='task_priority'),
        default='中'
    )
    assigned_to = Column(String(100))
    due_date = Column(Date)

    # Relationships
    process = relationship('Process', back_populates='tasks')
    workflow_from = relationship('Workflow', foreign_keys='Workflow.from_task_id', back_populates='from_task')
    workflow_to = relationship('Workflow', foreign_keys='Workflow.to_task_id', back_populates='to_task')
    instances = relationship('TaskInstance', back_populates='task')
    steps = relationship('TaskStep', back_populates='task') 