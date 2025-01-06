# Created: dylannguyen
import io
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from fastapi import File, UploadFile
from app.constant.config import AZURE_BLOB_ACCOUNT_NAME, AZURE_BLOB_CONTAINER_NAME, AZURE_BLOB_KEY, AZURE_BLOB_URI
from azure.core.credentials import AzureNamedKeyCredential
from pypdf import PdfReader, PdfWriter
from fastapi import Depends, HTTPException, status
from azure.core.exceptions import ResourceNotFoundError
class AzureBlobHelper:
    def __init__(self):
        self.container_name = AZURE_BLOB_CONTAINER_NAME
        self.account_name = AZURE_BLOB_ACCOUNT_NAME
        self.account_key = AZURE_BLOB_KEY
        self.credential = AzureNamedKeyCredential(self.account_name, self.account_key)
    
    # code to list blobs in a container
    async def list_blob(self):
        blob_service_client = BlobServiceClient(account_url=AZURE_BLOB_URI,credential=self.credential)
        container_client = blob_service_client.get_container_client(self.container_name)
        blob_list = container_client.list_blobs()
        return [blob.name for blob in blob_list]


    # code to generate SAS URL for a blob
    def generate_sas_url(self, blob_name):
        if not blob_name.lower().endswith('.pdf'):
            return None

        sas_blob = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=2) # Token valid for 2 hour
        )  
        print("check")
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_blob}"
    
    async def check_pdf(self, filename):
        filename = filename.lower()
        if filename.endswith(".pdf"):
            return True
        else:
            return False
        
    # If the file is a PDF, split into pages and upload each page
    async def upload_blob(self, upload_file: UploadFile) -> None:
        blob_service_client = BlobServiceClient(account_url=AZURE_BLOB_URI, credential=self.credential)
        blob_container = blob_service_client.get_container_client(self.container_name)
        
        if not blob_container.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Container not found"
            ) 
            
        file_bytes = await upload_file.read()
        file_name = upload_file.filename
        if file_name.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = reader.pages
            for i, page in enumerate(pages):
                blob_name = blob_name_from_file_page(file_name, i)
                
                page_io = io.BytesIO()
                writer = PdfWriter()
                writer.add_page(page)
                writer.write(page_io)
                page_io.seek(0)
                blob_container.upload_blob(name=blob_name, data=page_io, overwrite=True)
        else:
            blob_name = blob_name_from_file_page(file_name)
            blob_container.upload_blob(name=blob_name, data=io.BytesIO(file_bytes), overwrite=True)
    
        
    async def delete_blob(self, upload_file: UploadFile) -> None:
        blob_service_client = BlobServiceClient(account_url=AZURE_BLOB_URI, credential=self.credential)
        blob_container = blob_service_client.get_container_client(self.container_name)
        
        if not blob_container.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Container not found"
            ) 
        
        file_name = upload_file.filename
        file_bytes = await upload_file.read()
        
        # delete pdf pages
        if file_name.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(file_bytes))
            num_pages = len(reader.pages)

            for page in range(num_pages):
                blob_name = blob_name_from_file_page(filename=file_name, page=page)
                try:
                    blob_container.delete_blob(blob_name)
                except ResourceNotFoundError:
                    continue
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        detail=f"Failed to delete blob {blob_name}: {e}"
                    )
        else:
            blob_name = blob_name_from_file_page(filename=file_name)
            try:
                blob_container.delete_blob(blob_name)
            except ResourceNotFoundError:
                pass
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail=f"Failed to delete blob {blob_name}: {e}"
                )
                
def blob_name_from_file_page(filename: str, page: int =0):
        if os.path.splitext(filename)[1].lower() == ".pdf":
            return f"{os.path.splitext(os.path.basename(filename))[0]}-{page + 1}.pdf"
        else:
            return f"{os.path.basename(filename)}"