"""
TaskInstance model implementation
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship

from taskman.models.base import BaseModel

class TaskInstance(BaseModel):
    """
    TaskInstance model representing an instance of a task execution
    """
    __tablename__ = 'task_instance'

    id = Column(Integer, primary_key=True)
    process_instance_id = Column(Integer, ForeignKey('process_instance.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    status = Column(
        Enum('未着手', '実行中', '完了', '中断', '失敗', name='task_instance_status'),
        default='未着手'
    )
    assigned_to = Column(String(100))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text)

    # Relationships
    process_instance = relationship('ProcessInstance', back_populates='task_instances')
    task = relationship('Task', back_populates='instances') 