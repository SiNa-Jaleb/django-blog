# from django_resized import ResizedImageField
from django.contrib.auth.models import User
from django.contrib.staticfiles import storage
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django_jalali.db import models as jmodels
import os.path



# Manager
class PublishManger(models.Manager):
    def get_queryset(self):
        return Post.objects.filter(status=Post.Status.PUBLISHED)

class PublishCommentManger(models.Manager):
    def get_queryset(self):
        return Comment.objects.filter(active=True)



# Create your models here.

class Post(models.Model):
    # Choices
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"
        REJECTED = "RJ", "Rejected"

    CATEGORY_CHOICES = (
        ("برنامه نویسی", "برنامه نویسی"),
        ("تکنولوژی", "تکنولوژی"),
        ("هوش مصنوعی", "هوش مصنوعی"),
        ("بازی", "بازی"),
        ("سایر", "سایر"),
    )
    # Post fields
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name="posts", verbose_name="نویسنده")
    title = models.CharField(max_length=250, verbose_name="تایتل")
    description = models.TextField(verbose_name="توضیحات")
    slug = models.CharField(max_length=250, verbose_name="اسلاگ")
    publish = jmodels.jDateTimeField(default=timezone.now, verbose_name="تاریخ انتشار")
    create = jmodels.jDateTimeField(auto_now_add=True)
    update = jmodels.jDateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name="وضعیت"
    )
    study = models.PositiveIntegerField(verbose_name="زمان مطالعه")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="سایر", verbose_name="دسته بندی")

    objects = jmodels.jManager()
    published = PublishManger()

    class Meta:
        ordering = ["-publish"]
        indexes = [models.Index(fields=["-publish"])]
        verbose_name = "پست"
        verbose_name_plural = "پست ها"

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        for img in self.images.all():
            storage , path = img.image_file.storage, img.image_file.path
            storage.delete(path)
        super().delete(*args, **kwargs)


    def __str__(self):
        return self.title
    

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.id])
    


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images", verbose_name="پست")
    title = models.CharField(max_length=250, verbose_name="تایتل", null=True, blank=True)
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    create = jmodels.jDateTimeField(auto_now_add=True)
    # image_file = ResizedImageField(upload_to="images/", size=(800, 600), crop=['center', 'center'],quality=70, verbose_name="تصویر")
    image_file = models.ImageField(upload_to="images/", verbose_name="تصویر")

    class Meta:
        ordering = ["create"]
        indexes = [models.Index(fields=["create"])]
        verbose_name = "تصویر"
        verbose_name_plural = "تصاویر"


    def delete(self, *args, **kwargs):
        storage, path = self.image_file.storage, self.image_file.path
        storage.delete(path)
        super().delete(*args, **kwargs)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return os.path.basename(self.image_file.name)
        

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="comments", verbose_name="پست")
    author = models.CharField(max_length=250, verbose_name="نویسنده کامنت")
    text = models.TextField(verbose_name="متن کامنت")
    create = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    active = models.BooleanField(db_default=False, verbose_name="فعال")

    objects = jmodels.jManager()
    published = PublishCommentManger()

    class Meta:
        ordering = ["-create"]
        indexes = [models.Index(fields=["-create"])]
        verbose_name = "کامنت"
        verbose_name_plural = "کامنت ها"

    def __str__(self):
        return f"{self.author} : {self.post}"
    

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account", verbose_name="کاربر")
    job = models.CharField(max_length=250, verbose_name="شغل", null=True, blank=True)
    bio = models.TextField(verbose_name="بایو", null=True, blank=True)
    photo = models.ImageField(upload_to="avatar/", null=True, blank=True)

    class Meta:
        verbose_name="اکانت"
        verbose_name_plural="اکانت ها"

    def __str__(self):
        return self.user.username


class Ticket(models.Model):
    class Status(models.TextChoices):
        REVIEW = "RE", "Review"
        CHECK = "Ch", "Check"

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets", verbose_name="فرستنده")
    message = models.TextField(verbose_name="متن")
    subject = models.CharField(max_length=250, verbose_name="موضوع")
    problem = models.CharField(max_length=250, verbose_name="مشکل")
    creat = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.REVIEW, verbose_name="وضعیت")

    class Meta:
        ordering=["-creat"]
        indexes = [models.Index(fields=["-creat"])]
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت ها"

    def delete(self, *args, **kwargs):
        for img in self.images.all():
            storage, path = img.image_file.storage, img.image_file.path
            storage.delete(path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.subject


class TicketImage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="images", verbose_name="تیکت")
    title = models.CharField(max_length=250, verbose_name="تایتل", null=True, blank=True)
    create = jmodels.jDateTimeField(auto_now_add=True)
    image_file = models.ImageField(upload_to="images/ticket/", verbose_name="تصویر")

    class Meta:
        ordering = ["create"]
        indexes = [models.Index(fields=["create"])]
        verbose_name = "تصویر تیکت"
        verbose_name_plural = "تصاویر تیکت"
