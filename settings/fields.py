import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.fields.files import ImageField, ImageFieldFile

class CompressedImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        try:
            # Open the uploaded image using Pillow
            img = Image.open(content)
        except Exception as e:
            # Fallback: if the image can't be processed, use the original file
            super().save(name, content, save)
            return

        # Convert to RGB (if necessary) for JPEG compatibility
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Optionally resize the image if width is greater than max_width
        max_width = 1200
        if img.width > max_width:
            # Using thumbnail preserves aspect ratio in place
            # Set max height high enough so that width is the limiting factor
            img.thumbnail((max_width, 10000), Image.LANCZOS)

        # Save the image to an in-memory file (BytesIO)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=70, optimize=True)
        output.seek(0)

        # Create a new InMemoryUploadedFile from the BytesIO object
        new_content = InMemoryUploadedFile(
            output,
            field_name=self.field.name,
            name=name,
            content_type='image/jpeg',
            size=output.getbuffer().nbytes,
            charset=None
        )
        super().save(name, new_content, save)

class CompressedImageField(ImageField):
    attr_class = CompressedImageFieldFile
