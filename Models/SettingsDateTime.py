from  sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, \
    String, Integer, ForeignKey, func, TIMESTAMP, Boolean, Date, extract
Base = declarative_base()

class SettingsDateTime(Base):
    __tablename__ = 'state_notification'
    id = Column(Integer, primary_key=True)
    notificationid = Column(Integer)
    currentstate = Column(String)
    state = Column(Boolean)
    createdatetime = Column(DateTime)

from sqlalchemy import create_engine
engine=create_engine('postgresql+psycopg2://postgres:2537300@localhost:5432/dashboards')
from  sqlalchemy.orm import sessionmaker
session=sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)