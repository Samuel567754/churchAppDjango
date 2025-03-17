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
    A custom Django storage backend that uploads files to Supabase Storage
    and returns public URLs.
    """
    def __init__(self, bucket_name=None):
        # Use the provided bucket name or fall back to the settings.
        self.bucket_name = bucket_name or getattr(settings, 'SUPABASE_STORAGE_BUCKET', None)
        if not self.bucket_name:
            raise ValueError("SUPABASE_STORAGE_BUCKET must be set in settings or passed as a parameter.")
        # Initialize the Supabase client.
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def _open(self, name, mode='rb'):
        """
        Retrieve a file from Supabase Storage using its public URL.
        """
        file_url = self.url(name)
        response = requests.get(file_url)
        if response.status_code != 200:
            raise IOError(f"Could not open file {name} from Supabase. Status code: {response.status_code}")
        return ContentFile(response.content)

    def _save(self, name, content):
        """
        Save a file to Supabase Storage using the original filename.
        If a file with the same name already exists, delete it and re-upload.
        """
        content.open()  # Reset file pointer to the beginning.
        file_data = content.read()
        try:
            response = self.supabase.storage.from_(self.bucket_name).upload(name, file_data)
        except StorageApiError as e:
            error_info = e.args[0] if e.args else {}
            if isinstance(error_info, dict) and error_info.get('error') == 'Duplicate':
                # File exists; delete it first.
                self.delete(name)
                response = self.supabase.storage.from_(self.bucket_name).upload(name, file_data)
            else:
                raise
        return name

    def exists(self, name):
        """
        Always return False so that _save() is always called.
        (This forces a new upload even if a file exists.)
        """
        return False

    def url(self, name):
        """
        Return the public URL for the file stored in Supabase.
        Handles both dictionary and string responses.
        """
        url_response = self.supabase.storage.from_(self.bucket_name).get_public_url(name)
        if isinstance(url_response, dict):
            public_url = url_response.get("data", {}).get("publicUrl")
        else:
            public_url = url_response

        if not public_url:
            raise Exception(f"Unable to retrieve public URL for file: {name}")
        return public_url

    def delete(self, name):
        """
        Delete the file from Supabase Storage.
        """
        try:
            self.supabase.storage.from_(self.bucket_name).remove([name])
        except StorageApiError as e:
            error_info = e.args[0] if e.args else {}
            if isinstance(error_info, dict) and error_info.get('error'):
                error_message = error_info.get('message', 'Unknown error')
                raise Exception(f"Supabase delete error: {error_message}")

    def size(self, name):
        """
        Return the size of the file (not implemented).
        """
        return 0

    def get_available_name(self, name, max_length=None):
        """
        Return the original file name (as _save uses the original name).
        """
        return name


    # def _normalize_name(self, name):
    #     """
    #     Normalize the file name.
    #     This method is not implemented here.
    #     """
    #     return name
    
    
    




# import time
# import uuid
# import requests
# from django.core.files.base import ContentFile
# from django.core.files.storage import Storage
# from django.conf import settings
# from django.utils.deconstruct import deconstructible
# from supabase import create_client, Client
# from storage3._sync.file_api import StorageApiError

# @deconstructible
# class SupabaseMediaStorage(Storage):
#     """
#     A custom Django storage backend that uploads files to Supabase Storage
#     using unique filenames and returns their public URLs.
#     """
#     def __init__(self, bucket_name=None):
#         # Use the provided bucket name or fall back to the settings.
#         self.bucket_name = bucket_name or getattr(settings, 'SUPABASE_STORAGE_BUCKET', None)
#         if not self.bucket_name:
#             raise ValueError("SUPABASE_STORAGE_BUCKET must be set in settings or passed as a parameter.")
#         # Initialize the Supabase client.
#         self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

#     def _open(self, name, mode='rb'):
#         """
#         Retrieve a file from Supabase Storage using its public URL.
#         """
#         file_url = self.url(name)
#         response = requests.get(file_url)
#         if response.status_code != 200:
#             raise IOError(f"Could not open file {name} from Supabase. Status code: {response.status_code}")
#         return ContentFile(response.content)

#     def _save(self, name, content):
#         """
#         Save a file to Supabase Storage using a unique filename.
#         The unique filename is generated by prepending the current timestamp and a UUID.
#         """
#         # Create a unique filename.
#         unique_name = f"{int(time.time())}_{uuid.uuid4().hex}_{name}"
#         content.open()  # Ensure the file pointer is at the beginning.
#         file_data = content.read()
#         try:
#             response = self.supabase.storage.from_(self.bucket_name).upload(unique_name, file_data)
#         except StorageApiError as e:
#             # If a duplicate error occurs, delete the existing file and try again.
#             error_info = e.args[0] if e.args else {}
#             if isinstance(error_info, dict) and error_info.get('error') == 'Duplicate':
#                 self.delete(unique_name)
#                 response = self.supabase.storage.from_(self.bucket_name).upload(unique_name, file_data)
#             else:
#                 raise
#         return unique_name

#     def exists(self, name):
#         """
#         Always return False to force Django to call _save(), which uploads a new file.
#         """
#         return False

#     def url(self, name):
#         """
#         Return the public URL for a file stored in Supabase.
#         This method handles responses that are either dictionaries or strings.
#         """
#         url_response = self.supabase.storage.from_(self.bucket_name).get_public_url(name)
#         if isinstance(url_response, dict):
#             public_url = url_response.get("data", {}).get("publicUrl")
#         else:
#             public_url = url_response
#         if not public_url:
#             raise Exception(f"Unable to retrieve public URL for file: {name}")
#         return public_url

#     def delete(self, name):
#         """
#         Delete a file from Supabase Storage.
#         """
#         try:
#             self.supabase.storage.from_(self.bucket_name).remove([name])
#         except StorageApiError as e:
#             error_info = e.args[0] if e.args else {}
#             if isinstance(error_info, dict) and error_info.get('error'):
#                 error_message = error_info.get('message', 'Unknown error')
#                 raise Exception(f"Supabase delete error: {error_message}")

#     def size(self, name):
#         """
#         Return the size of the file.
#         (This method is not implemented here.)
#         """
#         return 0

#     def get_available_name(self, name, max_length=None):
#         """
#         Return the available file name.
#         Since _save() always generates a unique filename, just return the provided name.
#         """
#         return name
