"""
Process model implementation
"""
from sqlalchemy import Column, String, Text, Integer, Enum
from sqlalchemy.orm import relationship

from taskman.models.base import BaseModel
from taskman.models.process_instance import ProcessInstance
from taskman.models.mapping import objective_process_mapping

class Process(BaseModel):
    """
    Process model representing a workflow process
    """
    __tablename__ = 'process'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(Integer, default=1)
    status = Column(
        Enum('アクティブ', '非アクティブ', 'ドラフト', name='process_status'),
        default='ドラフト'
    )

    # Relationships
    objectives = relationship('Objective', secondary=objective_process_mapping, back_populates='processes')
    tasks = relationship('Task', back_populates='process')
    workflow = relationship('Workflow', back_populates='process')
    instances = relationship('ProcessInstance', back_populates='process') 