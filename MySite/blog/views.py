from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import random

# Create your views here.


def index(request):
    posts = Post.published.all()
    random_post = random.choice(posts)
    return render(request, "blog/index.html", {"random_post": random_post})


def post_list(request, category=None, tag_slug=None):
    if category is not None:
        posts = Post.published.filter(category=category)
    elif tag_slug is not None:
        posts = Post.objects.filter(tags__slug=tag_slug)
    else:
        posts = Post.published.all()

    paginator = Paginator(posts, 4)
    page_number = request.GET.get("page", 1)

    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)

    context = {"posts": posts, "category": category}

    return render(request, "blog/post_list.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    form = CommentForm()
    comments = post.comments.filter(active=True)
    context = {"post": post, "form": form, "comments": comments}
    return render(request, "blog/post_detail.html", context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    comment = None
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    context = {"comment": comment, "form": form, "post": post}
    return render(request, "form/comment_validation.html", context)


def search(request):
    result = []
    query = None
    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            search_query = SearchQuery(query)
            search_vector = (
                SearchVector("title", weight="A")
                + SearchVector("tags__name", weight="A")
                + SearchVector("description", weight="B")
                + SearchVector("images__title", weight="B")
                + SearchVector("category", weight="C")
            )
            search_rank = SearchRank(search_vector, search_query)

            result = (
                Post.published.annotate(search=search_vector, rank=search_rank)
                .filter(search=search_query)
                .order_by("id", "-rank")
                .distinct("id")
            )

            result = sorted(result, key=lambda x: x.rank, reverse=True)
    context = {"result": result, "query": query}
    return render(request, "blog/search.html", context)


class LoginView_custom(LoginView):
    template_name = "registration/authentic.html"
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "نام کاربری یا رمز عبور اشتباه است!")
        return super().form_invalid(form)


@require_POST
def register(request):
    form = RegisterForm(request.POST)
    user = None
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()
        messages.success(
            request, "ثبت نام شما با موفقیت انجام شد. اکنون می‌توانید وارد شوید."
        )
        return redirect("blog:login")
    else:
        messages.error(request, "لطفاً خطاهای فرم ثبت‌نام را برطرف کنید.")

    context = {"form": form, "user": user, "active_tab": "signup"}
    return render(request, "registration/authentic.html", context)



@login_required
def profile(request):
    user = request.user
    posts = Post.objects.filter(author=user)
    comments = Comment.published.filter(post__author=user)
    context = {"user": user, "posts": posts, "comments":comments}
    return render(request, "blog/profile.html", context)


@login_required
@require_POST
def edit_account(request):
    user_form = UserEditForm(request.POST, request.FILES,instance=request.user)

    if user_form.is_valid():
        user_form.save()
        messages.success(request, "تغییرات با موفقیت انجام شد")
        return redirect("blog:profile")
    else:
        messages.error(request, "لطفا خطا های  زیر را برطرف کنید")

    context = {"user_form": user_form}
    return render(request, "blog/profile.html", context)


@login_required
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    messages.success(request, f"پست {post.title} با موفقیت حذف شد!")
    return redirect("blog:profile")


class PasswordChange(PasswordChangeView):
    template_name = "registration/password_change.html"
    success_url = reverse_lazy("blog:profile")

    def form_valid(self, form):
        messages.success(self.request, "رمز شما با موفقیت تغییر یافت")
        return super().form_valid(form)


@login_required()
def create_post(request):
    if request.method == "POST":
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            images = request.FILES.getlist('images')
            print(images)
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            for image in images:
                if image:
                    Image.objects.create(post=post, image_file=image)

            messages.success(request, "پست شما با موفقیت ایجاد شد. منتظر بررسی ادمین برای انتشار باشید")

            return redirect("blog:profile")
    else:
        post_form = PostForm()


    return render(request, "form/post.html", {"post_form": post_form})


@login_required()
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    images = Image.objects.filter(post=post)
    if request.method == "POST":
        post_form = PostForm(request.POST, instance=post)
        if post_form.is_valid():
            post_form.save()
            images_received = request.FILES.getlist('images')
            if images_received:
                for img in images_received:
                    Image.objects.create(post=post, image_file=img)

            messages.success(request, "تغییرات با موفقیت انجام شد.")
            return  redirect("blog:profile")

    else:
        post_form = PostForm(instance=post)

    context = {"post_form": post_form, "images": images}
    return render(request, "form/post.html", context)


@login_required()
def delete_photo(request, pk):
    photo = get_object_or_404(Image, id=pk)
    photo.delete()
    post = photo.post
    return redirect("blog:edit_post", post_id = post.id)


@login_required()
def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            tik = form.save(commit=False)
            tik.author = request.user
            tik.save()

            images_received = request.FILES.getlist("images")
            if images_received:
                for image in images_received:
                    TicketImage.objects.create(ticket=tik, image_file=image)

            messages.success(request, "تیکت با موفقیت ثبت شد")
            return  redirect("blog:profile")
    else:
        form = TicketForm()

    return render(request, "form/ticket.html", {"form": form})


def public_profile(request, pk):
    user = get_object_or_404(User, id=pk)
    posts = Post.published.filter(author=user)

    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "blog/public_profile.html", {"user": user, "posts": posts})
