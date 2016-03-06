from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Float
from app.extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    app_version = Column(String)
    language = Column(String)
