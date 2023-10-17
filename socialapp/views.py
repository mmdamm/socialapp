from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse,JsonResponse
from django.core.mail import send_mail
from .forms import *
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery, TrigramSimilarity


# Create your views here.


def log_out(request):
    logout(request)
    return HttpResponse('you are logout')


def profile(request):
    author = request.user.username
    posts = Post.objects.filter(author__username=author)
    context = {
        'author': author,
        'posts': posts
    }

    return render(request, 'social/profile.html', context)


def ticket(request):
    sent = False
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            message = f"{cd['name']}\n{cd['email']}\n{cd['phone']}\n\n{cd['message']}"
            send_mail(cd['subject'], message, 'mohammad2547mohseny@gamil.com', ['mmhsny429@gamil.com'],
                      fail_silently=False)
            sent = True

    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form, 'sent': sent})


def register(request):
    if request.method == 'POST':
        form = UserRigesterForm(request.POST)
        if form.is_valid():
            user = form.save(
                commit=False)  # da vaghe chon dar form in ghestmat password v password 2 darim v dakhel fild nistan va khodemon igadesh kardim inga faght ye save mizanim v ba commit=false nemisarim dar database igad beshe faghat igad mishe ke on fild haye password ro meghdar dehi v baresi konim
            user.set_password(form.cleaned_data['password'])
            user.save()  # v hala inga dige save kamel ro mizanim ta dar database ham igad beshe
            Account.objects.create(
                user=user)  # har karbari ke sabtnam mikone dar vaghe bayadd yek accnout ham barash sakhte  beshe
            return render(request, 'registration/register_done.html', {'user': user})
    else:
        form = UserRigesterForm()
    return render(request, 'registration/register.html', {'form': form})


def edit_account(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        account_form = AccountEditForm(request.POST, instance=request.user.account, files=request.FILES)
        if account_form.is_valid() and user_form.is_valid():
            account_form.save()
            user_form.save()
            return redirect('socialapp:profile')
    else:
        user_form = UserEditForm(instance=request.user)
        account_form = AccountEditForm(instance=request.user.account)
    context = {
        'account_form': account_form,
        'user_form': user_form
    }
    return render(request, 'registration/edit_account.html', context)


def post_list(request, tag_slug=None):
    posts = Post.objects.all()
    tag = None
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
                filter(similarity__gt=0.1).order_by('-similarity')# darage sacht giri

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

