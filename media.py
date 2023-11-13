from datetime import datetime
from pydantic import BaseModel
class Media(BaseModel):
	name: str
	description: str
	date_of_media: datetime | None
	keywords: list[str]
	object_url: str
	
	# def __init__(self):
	