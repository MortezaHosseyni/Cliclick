"""
Support chat models
مدل‌های گفتگوی پشتیبانی
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class SupportChat(Base):
    """Support chat model / مدل گفتگوی پشتیبانی"""
    __tablename__ = "support_chats"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(255))  # Chat subject / موضوع گفتگو
    status = Column(String(50), default="Open")  # Open, Closed / باز، بسته
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships / روابط
    patient_user = relationship("User", back_populates="support_chats")
    messages = relationship("SupportMessage", back_populates="chat", cascade="all, delete-orphan")


class SupportMessage(Base):
    """Support message model / مدل پیام پشتیبانی"""
    __tablename__ = "support_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("support_chats.id"), nullable=False)
    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships / روابط
    chat = relationship("SupportChat", back_populates="messages")