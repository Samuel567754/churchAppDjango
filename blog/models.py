from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils.timezone import now
from contact.models import SocialMediaMixin, ImageMixin
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
from settings.fields import CompressedImageField


# BLOG
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the category")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated slug for the category URL")
    description = models.TextField(blank=True, help_text="Optional description of the category")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the category was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the category was last updated")

    class Meta:
        verbose_name_plural = "blog categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Name of the tag")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated slug for the tag URL")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
       if not self.slug:
            self.slug = slugify(self.name)
       super().save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the blog post")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated slug for the post URL")
    author = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Author of the blog post")
    # content = models.TextField(help_text="Content of the blog post")
    content = CKEditor5Field(config_name='extends')  # Use CKEditor 5
    featured_image = CompressedImageField(upload_to='blog/', blank=True, null=True, help_text="Optional featured image for the post")
    categories = models.ManyToManyField(Category, related_name='posts', help_text="Categories the post belongs to")
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True, help_text="Tags for the blog post")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the post was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the post was last updated")
    is_published = models.BooleanField(default=False, help_text="Indicates if the blog post is published")
    published_at = models.DateTimeField(null=True, blank=True, help_text="Date and time the blog post was published")
    views_count = models.IntegerField(default=0, help_text="Number of views for the blog post")
    meta_description = models.CharField(max_length=160, blank=True, help_text="Meta description for SEO")
    featured = models.BooleanField(default=False, help_text="Indicates if the blog post is featured")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = now()
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', help_text="The blog post this comment belongs to")
    author = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Author of the comment")
    content = models.TextField(help_text="Content of the comment")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the comment was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the comment was last updated")
    is_approved = models.BooleanField(default=False, help_text="Indicates if the comment has been approved")

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


# class Like(models.Model):
    
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', help_text="The blog post that has been liked")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', help_text="User that liked the blog post")
#     liked_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the like was added")

#     class Meta:
#         unique_together = ('post', 'user')

#     def __str__(self):
#         return f"{self.user.username} likes {self.post.title}"

class Like(models.Model):
    LIKE_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    
    post = models.ForeignKey(
        'Post', on_delete=models.CASCADE, related_name='likes',
        help_text="The blog post that has been liked or disliked"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes',
        help_text="User that liked or disliked the blog post"
    )
    like_type = models.CharField(
        max_length=10, choices=LIKE_CHOICES, default='like',
        help_text="Indicates whether the user liked or disliked the post"
    )
    liked_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the like or dislike was added")

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} {self.like_type}s {self.post.title}"


# Signals
@receiver(pre_save, sender=Category)
def set_category_slug(sender, instance, **kwargs):
    """
    Automatically sets the slug for a category before saving.
    """
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=Tag)
def set_tag_slug(sender, instance, **kwargs):
    """
    Automatically sets the slug for a tag before saving.
    """
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=Post)
def set_post_slug(sender, instance, **kwargs):
    """
    Automatically sets the slug for a post before saving.
    """
    if not instance.slug:
        instance.slug = slugify(instance.title)
    if instance.is_published and not instance.published_at:
      instance.published_at = now()