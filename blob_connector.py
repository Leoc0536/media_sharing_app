import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient


def connect(self):
	load_dotenv()
	storage_account_key = os.getenv('storage_account_key')
	storage_account_name = os.getenv('storage_account_name')
	connection_string = os.getenv('connection_string')
	container_name = os.getenv('container_name')

	service = BlobServiceClient.from_connection_string(conn_str=connection_string)
	# service.list_containers() returns iterable
	for _ in service.list_containers():
		print(_)
	# service.get_container_client() returns iterable
	container_client = service.get_container_client(container_name)
	for _ in container_client.list_blob_names():
		print(_)

	try:
		container_client = service.get_container_client(container=container_name)
		container_client.get_container_properties()
	except Exception as e:
		print(e)
		print("Creating container...")
		container_client = service.create_container(container_name)
	service.close()
	return container_client

def get_image(self):
	blob = BlobConnector()
	container = blob.connect()
	blob_items = container.list_blobs()
	images = []
	videos = []
	for blob in blob_items:
		blob_client = container.get_blob_client(blob=blob.name)
		if blob.name.endswith(('.png', '.jpeg', '.jpg', '.gif')):
			images.append(blob_client.url)
	return []

	