import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient


load_dotenv()
storage_account_key = os.getenv('storage_account_key')
storage_account_name = os.getenv('storage_account_name')
connection_string = os.getenv('connection_string')
container_name = os.getenv('container_name')

service = BlobServiceClient.from_connection_string(conn_str=connection_string)

blob = service.get_blob_client(container_name, blob="big_5b252c1a32b7d copy 2.jpg")
print(blob.url)
# container_client = service.get_container_client(container_name)
# for _ in container_client.list_blob_names():
# 	blob = container_client.get_blob_client(_)
# 	d = blob.get_blob_properties()
# 	print(blob.url)
	# https: // cs11003200228176c86.blob.core.windows.net / test / test.jpg
	# https: // cs11003200228176c86.blob.core.windows.net / test / big_5b252c1a32b7d.jpg
	# print(_)
# try:
# 	container_client = service.get_container_client(container=container_name)
# 	container_client.get_container_properties()
# except Exception as e:
# 	print(e)
# 	print("Creating container...")
# 	container_client = service.create_container(container_name)
service.close()
# return container_client




def blob_connect():
	BlobServiceClient.from_connection_string(connection_string)
	
	return