from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from .forms import *
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery, TrigramSimilarity
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages


# Create your views here.


def log_out(request):
    logout(request)
    return HttpResponse('you are logout')


def profile(request):
    author = User.objects.prefetch_related('followers').get(id=request.user.id)
    saved_posts = author.save_post.all()
    posts = Post.objects.filter(author__username=author)
    context = {
        'author': author,
        'posts': posts,
        'saved_posts': saved_posts
    }

    return render(request, 'social/profile.html', context)


def ticket(request):
    # sent = False
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            message = f"{cd['name']}\n{cd['email']}\n{cd['phone']}\n\n{cd['message']}"
            send_mail(cd['subject'], message, 'mohammad2547mohseny@gamil.com', ['mmhsny429@gamil.com'],
                      fail_silently=False)
            messages.success(request, 'Your comment has been sent successfully. ')
            messages.error(request, 'Error')
            messages.warning(request,'warning!!!')
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRigesterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return render(request, 'registration/register_done.html', {'user': user})
    else:
        form = UserRigesterForm()
    return render(request, 'registration/register.html', {'form': form})


def post_list(request, tag_slug=None):
    posts = Post.objects.select_related('author').order_by('-total_likes')
    tag = None
    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 2)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = []
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'social/list_ajax.html', {'posts': posts})
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tag__in=[tag])
    context = {
        'posts': posts,
        'tag': tag,
    }
    return render(request, "social/list.html", context)


def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('socialapp:profile')
    else:
        form = CreatePostForm()
    return render(request, 'forms/create_post.html', {'form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    post_tags_id = post.tag.values_list('id', flat=True)
    similar_post = Post.objects.filter(tag__in=post_tags_id).exclude(id=pk)
    similar_post = similar_post.annotate(same_tag=Count('tag')).order_by('-same_tag', '-created')[:2]
    context = {
        'post': post,
        'similar_post': similar_post
    }
    return render(request, 'social/detail.html', {'post': post, 'similar_post': similar_post})


def post_comment_user(request, post_id):
    post = Comment.objects.filter(post_id=post_id, active=True)
    return render(request, 'social/post-comment.html', {'post': post, 'post_id': post_id})


def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'post': post,
        'form': form,
        'comment': comment,
        'post_id': post_id
    }
    return render(request, "forms/comment.html", context)


def post_search(request):
    query = None
    result = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_query = SearchQuery(query)
            result1 = Post.objects.filter(tag__name__in=[query])
            result2 = Post.objects.annotate(similarity=TrigramSimilarity('description', query)). \
                filter(similarity__gt=0.1).order_by('-similarity')  # Degree of strictness

            context = {
                'query': query,
                'result1': result1,
                'result2': result2,
            }

    return render(request, 'social/search.html', context)


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CreatePostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
            # Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
            return redirect('socialapp:post_list')
    else:
        form = CreatePostForm(instance=post)
    return render(request, 'forms/edit_post.html', {'form': form, 'post': post})


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect("socialapp:post_list")
    return render(request, 'forms/delete_post.html', {'post': post})


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True

        post_likes_count = post.likes.count()
        response_data = {
            'liked': liked,
            'likes_count': post_likes_count,
        }
    else:
        response_data = {'error': 'Invalid post_id'}

    return JsonResponse(response_data)


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = Post.objects.get(id=post_id)
        user = request.user

        if user in post.saved.all():
            post.saved.remove(user)
            saved = False
        else:
            post.saved.add(user)
            saved = True

        return JsonResponse({'saved': saved})
    return JsonResponse({'error': 'Invalid request'})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'user/user_list.html', {'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'user/user_detail.html', {'user': user})
