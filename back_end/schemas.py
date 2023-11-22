from datetime import datetime
from pydantic import BaseModel


class Keyword(BaseModel):
	keyword: str


class Media(BaseModel):
	name: str
	description: str
	date_of_media: datetime | None
	# keyword: list[Keyword] = []
	object_url: str
	
	
