"""
ProcessInstance model implementation
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from taskman.models.base import BaseModel
from taskman.models.task_instance import TaskInstance

class ProcessInstance(BaseModel):
    """
    ProcessInstance model representing an instance of a process execution
    """
    __tablename__ = 'process_instance'

    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    status = Column(
        Enum('実行中', '完了', '中断', '失敗', name='process_instance_status'),
        default='実行中'
    )
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_by = Column(String(100))

    # Relationships
    process = relationship('Process', back_populates='instances')
    task_instances = relationship('TaskInstance', back_populates='process_instance') 