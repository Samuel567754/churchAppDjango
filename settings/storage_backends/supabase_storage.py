import time
import uuid
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.conf import settings
from django.utils.deconstruct import deconstructible
from supabase import create_client, Client
from storage3._sync.file_api import StorageApiError

@deconstructible
class SupabaseMediaStorage(Storage):
    """
    A custom Django storage backend that uploads files to Supabase Storage using unique filenames
    and returns public URLs.
    """
    def __init__(self, bucket_name=None):
        self.bucket_name = bucket_name or getattr(settings, 'SUPABASE_STORAGE_BUCKET', None)
        if not self.bucket_name:
            raise ValueError("SUPABASE_STORAGE_BUCKET must be set in settings or passed as a parameter.")
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def _open(self, name, mode='rb'):
        file_url = self.url(name)
        response = requests.get(file_url)
        if response.status_code != 200:
            raise IOError(f"Could not open file {name} from Supabase. Status code: {response.status_code}")
        return ContentFile(response.content)

    def _save(self, name, content):
        unique_name = f"{int(time.time())}_{uuid.uuid4().hex}_{name}"
        content.open()  # Ensure file pointer is at the beginning.
        file_data = content.read()
        try:
            response = self.supabase.storage.from_(self.bucket_name).upload(unique_name, file_data)
        except StorageApiError as e:
            error_info = e.args[0] if e.args else {}
            if isinstance(error_info, dict) and error_info.get('error') == 'Duplicate':
                self.delete(unique_name)
                response = self.supabase.storage.from_(self.bucket_name).upload(unique_name, file_data)
            else:
                raise
        return unique_name

    def exists(self, name):
        return False

    def url(self, name):
        url_response = self.supabase.storage.from_(self.bucket_name).get_public_url(name)
        if isinstance(url_response, dict):
            public_url = url_response.get("data", {}).get("publicUrl")
        else:
            public_url = url_response
        if not public_url:
            raise Exception(f"Unable to retrieve public URL for file: {name}")
        return public_url

    def delete(self, name):
        try:
            self.supabase.storage.from_(self.bucket_name).remove([name])
        except StorageApiError as e:
            error_info = e.args[0] if e.args else {}
            if isinstance(error_info, dict) and error_info.get('error'):
                error_message = error_info.get('message', 'Unknown error')
                raise Exception(f"Supabase delete error: {error_message}")

    def size(self, name):
        return 0

    def get_available_name(self, name, max_length=None):
        return name
