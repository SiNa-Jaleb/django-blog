from django.contrib import admin
from .models import *
from django_jalali.admin.filters import JDateFieldListFilter


# inlines
class ImageInline(admin.StackedInline):
    model = Image
    extra = 0


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0


class TicketImageInline(admin.StackedInline):
    model = TicketImage
    extra = 0

# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "publish", "status"]
    list_editable = ["category", "status"]
    list_filter = [("publish", JDateFieldListFilter), "status", "author"]
    ordering = ["-publish"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ["title"]}
    raw_id_fields = ["author"]
    date_hierarchy = "publish"
    inlines = [ImageInline, CommentInline]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["post", "title", "create"]
    raw_id_fields = ["post"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "author", "create", "active"]
    list_editable = ["active"]
    list_filter = ["active", "author", "post"]
    search_fields = ["author", "text"]

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["user", "job", "photo"]
    search_fields = ["user"]
    raw_id_fields = ["user"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["subject", "author", "creat","status"]
    list_editable = ["status"]
    inlines = [TicketImageInline]
