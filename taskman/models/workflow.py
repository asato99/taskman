"""
Workflow model implementation
"""
from sqlalchemy import Column, Integer, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

from taskman.models.base import BaseModel

class Workflow(BaseModel):
    """
    Workflow model representing task transitions
    """
    process_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    from_task_id = Column(Integer, ForeignKey('task.id'))
    to_task_id = Column(Integer, ForeignKey('task.id'))
    condition_type = Column(
        Enum('常時', '条件付き', '並列', name='workflow_condition'),
        default='常時'
    )
    condition_expression = Column(Text)
    sequence_number = Column(Integer)

    # Relationships
    process = relationship('Process', back_populates='workflow')
    from_task = relationship('Task', foreign_keys=[from_task_id], back_populates='workflow_from')
    to_task = relationship('Task', foreign_keys=[to_task_id], back_populates='workflow_to') 