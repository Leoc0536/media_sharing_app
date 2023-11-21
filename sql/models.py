from sqlalchemy import Column, String, Date, ARRAY, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .database import Base


class Media(Base):
	__tablename__ = 'media_metadata'
	
	id = Column(Integer, primary_key=True, index=True, default=1)
	name = Column(String(25), unique=True)
	description = Column(String(100))
	date_of_media = Column(Date)
	object_url = Column(String(255))
	# keyword = Column(String(25))
	
	keyword = relationship("Keyword", back_populates="key")


class Keyword(Base):
	__tablename__ = "keyword_table"
	
	id = Column(Integer, primary_key=True, index=True)
	keyword = Column(String(25))
	owner_id = Column(Integer, ForeignKey("media_metadata.id"))
	
	key = relationship("Media", back_populates="keyword")

