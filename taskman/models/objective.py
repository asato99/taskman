"""
Objective model implementation
"""
from sqlalchemy import Column, String, Text, Float, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship

from taskman.models.base import BaseModel
from taskman.models.mapping import objective_process_mapping

class Objective(BaseModel):
    """
    Objective model representing a goal or target
    """
    __tablename__ = 'objective'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    measure = Column(String(100))
    target_value = Column(Float)
    current_value = Column(Float)
    time_frame = Column(String(50))
    status = Column(
        Enum('進行中', '達成', '未達成', '中止', name='objective_status'),
        default='進行中'
    )
    parent_id = Column(Integer, ForeignKey('objective.id'), nullable=True)

    # Relationships
    parent = relationship('Objective', remote_side=[id], backref='sub_objectives')
    processes = relationship('Process', secondary=objective_process_mapping, back_populates='objectives') 