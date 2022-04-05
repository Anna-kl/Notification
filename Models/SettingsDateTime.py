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

engine=create_engine('postgresql://dufuauvnmhhnbi:e04834417d5b33baf80de46ff78c145979019532d52e0019de70b1e83dbf36b6@ec2-34-254-69-72.eu-west-1.compute.amazonaws.com:5432/ddq1javfo02shs')
from  sqlalchemy.orm import sessionmaker
session=sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)