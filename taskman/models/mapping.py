"""
Mapping tables for many-to-many relationships
"""
from sqlalchemy import Column, Integer, ForeignKey, Float, Table

from taskman.models.base import BaseModel

# Objective-Process mapping
objective_process_mapping = Table(
    'objective_process_mapping',
    BaseModel.metadata,
    Column('objective_id', Integer, ForeignKey('objective.id'), primary_key=True),
    Column('process_id', Integer, ForeignKey('process.id'), primary_key=True),
    Column('contribution_weight', Float)
) 