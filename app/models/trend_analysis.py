# app/models/trend_analysis.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.database import Base

class TrendAnalysis(Base):
    __tablename__ = "trend_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    query = Column(String(255), index=True)
    platform = Column(String(50), default="youtube")
    timestamp = Column(DateTime, default=func.now())
    trend_strength = Column(Float)
    trend_direction = Column(String(20))
    summary = Column(Text)
    insights = Column(Text)
    recommendations = Column(Text)
    plugin_insights = Column(Text, nullable=True)
    plugin_recommendations = Column(Text, nullable=True)
    metrics = Column(Text, nullable=True)
    full_response = Column(Text)
    
    def __repr__(self):
        return f"<TrendAnalysis(id={self.id}, query='{self.query}', platform='{self.platform}')>"