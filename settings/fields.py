import io
from PIL import Image
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.fields.files import ImageField, ImageFieldFile

# Helper functions to select storage backend based on environment.
def get_cloudinary_storage():
    if settings.DEBUG:
        # For development, use the local filesystem.
        return FileSystemStorage()
    # In production, use your Cloudinary storage backend.
    from settings.storage_backends.cloudinary_storage import CloudinaryMediaStorage
    return CloudinaryMediaStorage()

def get_supabase_storage():
    if settings.DEBUG:
        return FileSystemStorage()
    # In production, use your Supabase storage backend.
    from settings.storage_backends.supabase_storage import SupabaseMediaStorage
    return SupabaseMediaStorage()

# Custom field for images/videos with compression.
class CompressedImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        try:
            img = Image.open(content)
        except Exception as e:
            # If image processing fails, save the original file.
            super().save(name, content, save)
            return

        # Optionally, resize the image if its width is greater than max_width.
        max_width = 1200
        if img.width > max_width:
            img.thumbnail((max_width, 10000), Image.LANCZOS)

        output = io.BytesIO()
        # Determine the format: use PNG for images with transparency, otherwise JPEG.
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            output_format = 'PNG'
            content_type = 'image/png'
            img.save(output, format=output_format, optimize=True, compress_level=9)
        else:
            img = img.convert("RGB")
            output_format = 'JPEG'
            content_type = 'image/jpeg'
            img.save(output, format=output_format, quality=70, optimize=True)
        output.seek(0)

        new_content = InMemoryUploadedFile(
            output,
            field_name=self.field.name,
            name=name,
            content_type=content_type,
            size=output.getbuffer().nbytes,
            charset=None
        )
        super().save(name, new_content, save)

class CompressedImageField(ImageField):
    """
    A custom ImageField that compresses images before saving.
    In production, it uses Cloudinary storage; in development, it falls back to local storage.
    """
    attr_class = CompressedImageFieldFile

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('storage', get_cloudinary_storage())
        super().__init__(*args, **kwargs)

# Custom FileField for documents and other non-image files.
class SupabaseFileField(models.FileField):
    """
    A custom FileField that uses Supabase storage for non-image files.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('storage', get_supabase_storage())
        super().__init__(*args, **kwargs)





# import io
# from PIL import Image
# from django.core.files.uploadedfile import InMemoryUploadedFile
# from django.db.models.fields.files import ImageField, ImageFieldFile

# class CompressedImageFieldFile(ImageFieldFile):
#     def save(self, name, content, save=True):
#         try:
#             img = Image.open(content)
#         except Exception as e:
#             # Fallback: if image processing fails, use the original file
#             super().save(name, content, save)
#             return

#         # Optionally, resize the image if its width is greater than max_width
#         max_width = 1200
#         if img.width > max_width:
#             # thumbnail() preserves aspect ratio in place; using a high height so width is the constraint
#             img.thumbnail((max_width, 10000), Image.LANCZOS)

#         output = io.BytesIO()

#         # Check for transparency: if the image has an alpha channel or transparency info, save as PNG
#         if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
#             output_format = 'PNG'
#             content_type = 'image/png'
#             # Save as PNG (which supports transparency). You can adjust compress_level (0-9) if needed.
#             img.save(output, format=output_format, optimize=True, compress_level=9)
#         else:
#             # For non-transparent images, convert to RGB and save as JPEG
#             img = img.convert("RGB")
#             output_format = 'JPEG'
#             content_type = 'image/jpeg'
#             img.save(output, format=output_format, quality=70, optimize=True)
#         output.seek(0)

#         new_content = InMemoryUploadedFile(
#             output,
#             field_name=self.field.name,
#             name=name,
#             content_type=content_type,
#             size=output.getbuffer().nbytes,
#             charset=None
#         )
#         super().save(name, new_content, save)

# class CompressedImageField(ImageField):
#     attr_class = CompressedImageFieldFile







# import io
# from PIL import Image
# from django.core.files.uploadedfile import InMemoryUploadedFile
# from django.db.models.fields.files import ImageField, ImageFieldFile

# class CompressedImageFieldFile(ImageFieldFile):
#     def save(self, name, content, save=True):
#         try:
#             # Open the uploaded image using Pillow
#             img = Image.open(content)
#         except Exception as e:
#             # Fallback: if the image can't be processed, use the original file
#             super().save(name, content, save)
#             return

#         # Convert to RGB (if necessary) for JPEG compatibility
#         if img.mode in ("RGBA", "P"):
#             img = img.convert("RGB")

#         # Optionally resize the image if width is greater than max_width
#         max_width = 1200
#         if img.width > max_width:
#             # Using thumbnail preserves aspect ratio in place
#             # Set max height high enough so that width is the limiting factor
#             img.thumbnail((max_width, 10000), Image.LANCZOS)

#         # Save the image to an in-memory file (BytesIO)
#         output = io.BytesIO()
#         img.save(output, format='JPEG', quality=70, optimize=True)
#         output.seek(0)

#         # Create a new InMemoryUploadedFile from the BytesIO object
#         new_content = InMemoryUploadedFile(
#             output,
#             field_name=self.field.name,
#             name=name,
#             content_type='image/jpeg',
#             size=output.getbuffer().nbytes,
#             charset=None
#         )
#         super().save(name, new_content, save)

# class CompressedImageField(ImageField):
#     attr_class = CompressedImageFieldFile
