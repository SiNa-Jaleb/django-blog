from multiprocessing import context
from django import template
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from ..models import Post, Comment, User
from django.db.models import Count, Q
from django_jalali.templatetags.jformat import jformat
from markdown import markdown
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def total_post():
    return Post.published.count()


@register.simple_tag
def total_comment():
    return Comment.objects.filter(active=True).count()


@register.simple_tag
def total_user():
    return User.objects.filter(is_active=True).count()


@register.simple_tag
def last_post_date():
    date_l_post = Post.published.first().publish
    return jformat(date_l_post, "%Y/%m/%d")


@register.inclusion_tag("partials/most_active.html")
def most_active_user():
    user = User.objects.annotate(top_user=Count("posts")).order_by("-top_user")[0]
    context = {"user": user}
    return context


@register.inclusion_tag("partials/lastest_post.html")
def lastest_post(count=3):
    l_post = Post.published.prefetch_related("images", "tags").select_related("author").order_by("-publish")[:count]
    context = {"l_post": l_post}
    return context


@register.filter(name="markdown")
def to_markdown(text):
    return mark_safe(markdown(text))

@register.filter
def remove_markdown_sing(text):
    return text.replace("*","")


@register.inclusion_tag("partials/more_info_pp.html")
def more_info_pp(user_id):
    user = get_object_or_404(User.objects.annotate(
        t__study=Coalesce(
            Sum(
                "posts__study", filter=Q(posts__status=Post.Status.PUBLISHED)
            ),
            0
        ),
        total_post=Count("posts", filter=Q(posts__status=Post.Status.PUBLISHED)),
    ), id=user_id)
    context = {"total_post": user.total_post, "user": user}
    return context