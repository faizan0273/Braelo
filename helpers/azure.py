from azure.storage.blob import BlobServiceClient

blob_service_client = BlobServiceClient.from_connection_string(
    'DefaultEndpointsProtocol=https;AccountName=braelos3;AccountKey=ODvt'
    'b8NuHRyWRsNR54wyp2lP0a7YGlM//NnhbkQKKv+JhX9E9Z+JXUSX56/sY7q0OxYPjidA5'
    'HL0+AStWzRAYA==;EndpointSuffix=core.windows.net'
)
