from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from .models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import random

# Create your views here.


def index(request):
    posts = Post.published.all()
    random_post = random.choice(posts)
    return render(request, "blog/index.html", {"random_post": random_post})


def post_list(request, category=None, tag_slug=None):

    posts = Post.published.prefetch_related("tags", "images").select_related("author")
    if category is not None:
        posts = posts.filter(category=category)
    elif tag_slug is not None:
        posts = posts.filter(tags__slug=tag_slug)
    else:
        posts = posts.all()

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
    post = get_object_or_404(Post.published.prefetch_related("tags", "images", "likes").select_related("author"), id=post_id, status=Post.Status.PUBLISHED)
    form = CommentForm()
    comments = post.comments.filter(active=True).select_related("author")
    post_tags_id = post.tags.values_list("id", flat=True)
    similar_posts = (Post.published
                     .prefetch_related("images", "tags")
                     .select_related("author")
                     .annotate(same_tags=Count("tags", filter=Q(tags__id__in=post_tags_id)))
                     .exclude(id=post.id)
                     .order_by("-same_tags").filter(same_tags__gt=0)[:3])
    post_url = request.build_absolute_uri(post.get_absolute_url())
    context = {"post": post, "form": form, "comments": comments, "similar_posts":similar_posts, "post_url":post_url}
    return render(request, "blog/post_detail.html", context)


@login_required()
@require_POST
def post_comment(request):
    post_id = request.POST.get("post_id")
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    user = request.user
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = user
        comment.save()

        return JsonResponse({"status": "success",
            "message": "دیدگاه شما با موفقیت ثبت شد و پس از تایید مدیر نمایش داده خواهد شد."})

    return JsonResponse({"errors":form.errors.get_json_data()}, status=400)


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
                Post.published.prefetch_related("images", "tags").select_related("author").annotate(search=search_vector, rank=search_rank)
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
    comments = Comment.published.select_related("author", "post").filter(post__author=user)

    # pagination for load more in post list
    default_showing_post = posts[:4]
    show_more_post = posts[4:]
    paginator = Paginator(show_more_post, 2)
    page_num = request.GET.get("page",1)
    try:
        show_more_post = paginator.page(page_num)
    except PageNotAnInteger:
        show_more_post = paginator.page(1)
    except EmptyPage:
        show_more_post = []

    # pagination for load more in comments list
    default_showing_comment = comments[:6]
    show_more_comment = comments[6:]
    comment_paginator = Paginator(show_more_comment, 2)
    comment_page_num = request.GET.get("page",1)
    try:
        show_more_comment = comment_paginator.page(comment_page_num)
    except PageNotAnInteger:
        show_more_comment = comment_paginator.page(1)
    except:
        show_more_comment = []

    load = request.GET.get("load")
    # checking request if ajax for pagination
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if load == "posts":
            html = render_to_string("blog/post_list_ajax.html", {"show_more_post": show_more_post}, request)
            response_data = {"html": html, "has_next":show_more_post.has_next()}
            return JsonResponse(response_data)
        elif load == "comments":
            comment_html = render_to_string("blog/comment_list_ajax.html", {"show_more_comment":show_more_comment}, request)
            response_data = {"comment_html":comment_html, "has_next_comment":show_more_comment.has_next()}
            return JsonResponse(response_data)

    context = {"user": user, "default_showing_post": default_showing_post, "default_showing_comment":default_showing_comment, "has_more_post":paginator.count>0, "hase_more_comment":comment_paginator.count>0}
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


@require_POST
@login_required
def delete_post(request):
    post_id = request.POST.get("post_id")
    post = Post.objects.get(id=post_id)
    post.delete()
    response_data = {"post_id": post_id, "messages":f"پست {post.title} با موفقیت حذف شد!"}
    return JsonResponse(response_data)


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
            post_form.save_m2m()
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
@require_POST
def delete_post_photo(request):
    pk = request.POST.get("image_id")
    photo = get_object_or_404(Image, id=pk)
    photo.delete()
    response_data = {"image_id": pk}
    return JsonResponse(response_data)


@login_required()
def ticket(request):
    user = request.user
    tickets = user.tickets.all()

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            tik = form.save(commit=False)
            tik.author = user
            tik.save()

            images_received = request.FILES.getlist("images")
            if images_received:
                for image in images_received:
                    TicketImage.objects.create(ticket=tik, image_file=image)

            messages.success(request, "تیکت با موفقیت ثبت شد")
            return  redirect("blog:profile")
    else:
        form = TicketForm()

    return render(request, "form/ticket.html", {"form": form, "tickets":tickets})


@login_required()
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, "blog/ticket_detail.html", {"ticket": ticket})


def public_profile(request, pk):
    user = get_object_or_404(User, id=pk)
    posts = Post.published.prefetch_related("tags", "images").select_related("author").filter(author=user)

    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "blog/public_profile.html", {"user": user, "posts": posts})


@login_required()
@require_POST
def like_post(request):
    post_id = request.POST.get("post_id")
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
    total_likes = post.likes.count()
    response_data = {"liked": liked, "total_likes": total_likes}
    return JsonResponse(response_data)
