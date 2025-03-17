from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import now
from .models import Post, Category, Tag, Comment, Like
from .forms import CommentForm
from django.core.paginator import Paginator
from django.db.models import Count, Q, F
from bs4 import BeautifulSoup
from django.utils.safestring import mark_safe
from django.db import models


# 📌 Post List (Published Only)

def post_list(request):
    """
    Displays a list of all published blog posts.
    """
    posts = Post.objects.filter(is_published=True).order_by('-published_at')

    # Get the most recent published featured post
    featured_post = Post.objects.filter(is_published=True, featured=True).order_by('-published_at').first()

    # Get the 3 most recent published posts
    latest_posts = Post.objects.filter(is_published=True).order_by('-published_at')[:3]

    # Get all categories and tags
    categories = Category.objects.all()
    tags = Tag.objects.all()

    # Paginate the posts with 5 posts per page
    paginator = Paginator(posts, 5)  # 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get only the 3 most recent posts
    recent_posts = posts[:3]  

    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,  # Paginated posts
        'featured_post': featured_post,  # Featured post
        'latest_posts': latest_posts,  # Latest 3 posts
        'categories': categories,  # All categories
        'tags': tags,  # All tags
        'recent_posts': recent_posts,  # Recent 3 posts
    })
    
    
    
def extract_toc(content):
    """
    Extracts headings (h2, h3) from HTML content and returns a TOC list.
    """
    soup = BeautifulSoup(content, "html.parser")
    toc = []
    
    for tag in soup.find_all(['h2', 'h3']):  # Add more tags if needed
        if tag.text.strip():
            anchor = tag.text.lower().replace(" ", "-")  # Create a simple anchor
            tag['id'] = anchor  # Add an ID to each heading for linking
            toc.append({'level': tag.name, 'title': tag.text, 'anchor': anchor})

    return toc, str(soup)  # Return modified content with IDs
    
    
# 📌 Post Detail with Comments
def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects
        .select_related('author')
        .prefetch_related('categories', 'tags', 'comments')
        .filter(is_published=True)
        .annotate(
            like_count=Count('likes', filter=models.Q(likes__like_type='like')),
            dislike_count=Count('likes', filter=models.Q(likes__like_type='dislike')),
            comment_count=Count('comments')
        ),
        slug=slug
    )

    comments = post.comments.all()
    form = CommentForm()
    
    # Extract TOC
    toc, modified_content = extract_toc(post.content)
    post.content = mark_safe(modified_content)

    # User interactions
    user_like = None
    if request.user.is_authenticated:
        user_like = post.likes.filter(user=request.user).first()

        if request.method == 'POST':
            # Handle comment submission
            if 'submit_comment' in request.POST:
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.post = post
                    comment.author = request.user
                    comment.save()
                    messages.success(request, "Your comment is awaiting moderation.")
                    return redirect('blog:post_detail', slug=post.slug)

            # Handle like/unlike actions
            elif 'like_toggle' in request.POST:
                if user_like and user_like.like_type == 'like':
                    user_like.delete()
                    messages.info(request, "Removed your like from this post.")
                else:
                    Like.objects.update_or_create(user=request.user, post=post, defaults={'like_type': 'like'})
                    messages.success(request, "Thanks for liking this post!")
                return redirect('blog:post_detail', slug=post.slug)

            # Handle dislike action
            elif 'dislike_toggle' in request.POST:
                if user_like and user_like.like_type == 'dislike':
                    user_like.delete()
                    messages.info(request, "Removed your dislike from this post.")
                else:
                    Like.objects.update_or_create(user=request.user, post=post, defaults={'like_type': 'dislike'})
                    messages.success(request, "You disliked this post.")
                return redirect('blog:post_detail', slug=post.slug)

    # Related posts
    related_posts = Post.objects.filter(
        categories__in=post.categories.all(),
        is_published=True
    ).exclude(id=post.id).order_by('-published_at').distinct()[:3]

    # Increment view count
    Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    post.refresh_from_db()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'user_like': user_like,
        'like_count': post.like_count,
        'dislike_count': post.dislike_count,
        'comment_count': post.comment_count,
        'related_posts': related_posts,
        'meta_description': post.meta_description or getattr(post, 'content', '')[:160],
        'reading_time': max(1, len(post.content.split()) // 200),
        'table_of_contents': toc
    }
    return render(request, 'blog/post_detail.html', context)

# 📌 Filter Posts by Category


def posts_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(is_published=True, categories=category).order_by('-published_at')

    paginator = Paginator(posts, 5)  # Paginate with 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,
        'category': category,
        'categories': Category.objects.all(),  # For displaying categories in the sidebar
        'tags': Tag.objects.all(),  # For displaying tags
    })


def posts_by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(is_published=True, tags=tag).order_by('-published_at')

    paginator = Paginator(posts, 5)  # Paginate with 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,
        'tag': tag,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    })