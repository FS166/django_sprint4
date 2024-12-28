from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, \
    SetPasswordForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.utils.timezone import now
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, Http404
from django.template.loader import render_to_string
from django.conf import settings
from .models import Category, Post, Comment
from .utils import get_published_posts, paginate_queryset
from .forms import UserRegistrationForm, PostForm, EditProfileForm, CommentForm


class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse_lazy('blog:index')


def index(request):
    posts = get_published_posts().order_by('-pub_date')
    page_obj = paginate_queryset(posts, request)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    posts = get_published_posts().filter(category=category).order_by(
        '-pub_date')
    page_obj = paginate_queryset(posts, request)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
    })


def post_detail(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id
    )
    if not post.is_published:
        if post.author != request.user:
            raise Http404(
                "Убедитесь, что страница недоступна для других пользователей.")
    form = CommentForm()
    comments = post.comments.all().order_by('created_at')
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,
        'comments': comments,
    })


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_at = now()
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm(initial={'pub_date': now()})
    return render(request, 'blog/create.html', {'form': form})


def edit_post(request, post_id):
    if not request.user.is_authenticated:
        return redirect('login')
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Вы не можете удалить этот комментарий.")
    if request.method == "POST":
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {
        'form': form,
        'post': post,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_published=True)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail',
                            post_id=post.id)
    else:
        form = CommentForm()
    comments = post.comments.all().order_by(
        '-created_at')
    return render(request, 'includes/comments.html', {
        'post': post,
        'form': form,
        'comments': comments,
    })


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden(
            "Вы не можете редактировать чужие комментарии")
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html',
                  {'comment': comment, 'form': form})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Вы не можете удалить этот комментарий.")
    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {
        'comment': comment,
    })


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        print(request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile).order_by('-pub_date')
    page_obj = paginate_queryset(posts, request)
    return render(request, 'blog/profile.html',
                  {'profile': profile, 'page_obj': page_obj})


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            return redirect('blog:index')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/registration_form.html',
                  {'form': form})


def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    token = default_token_generator.make_token(user)
                    uid = user.pk
                    domain = get_current_site(request).domain
                    protocol = 'https' if request.is_secure() else 'http'
                    reset_link = (f"{protocol}://{domain}/auth/"
                                  f"password_reset_confirm/{uid}/{token}/")
                    message = render_to_string(
                        'registration/password_reset_email.html',
                        {'reset_link': reset_link}
                    )
                    send_mail(
                        "Сброс пароля",
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email]
                    )
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()

    return render(request, 'registration/password_reset_form.html',
                  {'form': form})


def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = int(uidb64)
        user = User.objects.get(pk=uid)
    except (ValueError, User.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'registration/password_reset_confirm.html',
                      {'form': form})
    else:
        return redirect('blog:index')


def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return render(request, 'registration/password_change_done.html')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'registration/password_change_form.html',
                  {'form': form})
