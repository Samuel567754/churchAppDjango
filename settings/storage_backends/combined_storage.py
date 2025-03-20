import os
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

# Import the two storage backends.
from settings.storage_backends.cloudinary_storage import CloudinaryMediaStorage
from settings.storage_backends.supabase_storage import SupabaseMediaStorage

@deconstructible
class CombinedDynamicStorage(Storage):
    """
    A dynamic Django storage backend that delegates to either CloudinaryMediaStorage
    or SupabaseMediaStorage based on the file extension.
    
    Files with extensions in `cloudinary_extensions` (e.g. images and videos)
    are stored using Cloudinary; all others are stored using Supabase.
    """
    def __init__(self):
        self.cloudinary_storage = CloudinaryMediaStorage()
        self.supabase_storage = SupabaseMediaStorage()
        # Define the file extensions that should be handled by Cloudinary.
        self.cloudinary_extensions = {
            "jpg", "jpeg", "png", "gif", "bmp", "webp",
            "mp4", "mov", "avi", "mkv"
        }
    
    def _get_backend_for_file(self, name):
        ext = os.path.splitext(name)[1].lower().strip('.')
        if ext in self.cloudinary_extensions:
            return self.cloudinary_storage
        return self.supabase_storage
    
    def _open(self, name, mode='rb'):
        backend = self._get_backend_for_file(name)
        return backend._open(name, mode)
    
    def _save(self, name, content):
        backend = self._get_backend_for_file(name)
        return backend._save(name, content)
    
    def exists(self, name):
        backend = self._get_backend_for_file(name)
        return backend.exists(name)
    
    def url(self, name):
        backend = self._get_backend_for_file(name)
        return backend.url(name)
    
    def delete(self, name):
        backend = self._get_backend_for_file(name)
        backend.delete(name)
    
    def size(self, name):
        backend = self._get_backend_for_file(name)
        return backend.size(name)
    
    def get_available_name(self, name, max_length=None):
        backend = self._get_backend_for_file(name)
        return backend.get_available_name(name, max_length)
