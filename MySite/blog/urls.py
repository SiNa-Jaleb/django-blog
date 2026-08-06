from . import views
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("post-list/", views.post_list, name="post_list"),
    path("post-list/<str:category>/", views.post_list, name="post_list_category"),
    path("post-list/tag/<tag_slug>", views.post_list, name="post_list_tag"),
    path("post-list/detail/<int:post_id>/", views.post_detail, name="post_detail"),
    path("post-list/detail/<int:post_id>/comment/", views.post_comment, name="post_comment"),
    path("search/",views.search, name="search"),
    path("profile/", views.profile, name="profile"),
    path("login/", views.LoginView_custom.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),

    path("edit-account/", views.edit_account, name="edit_account"),
    path("delete-post/<int:post_id>", views.delete_post, name="delete_post"),


    path('profile/password-change/', views.PasswordChange.as_view(), name="password_change" ),

    path("profile/create-post/", views.create_post, name="create_post"),
    path("profile/edit-post/<int:post_id>/", views.edit_post, name="edit_post"),
    path("profile/edit-post/delete-photo/<int:pk>", views.delete_photo, name="delete_photo"),


    path("password-reset/", auth_views.PasswordResetView.as_view(success_url=reverse_lazy('blog:password_reset_done')), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy("blog:password_reset_complete")), name="password_reset_confirm"),
    path("password-reset/complete/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path("profile/ticket/", views.ticket, name="ticket"),
    path("public-profile/<int:pk>/", views.public_profile, name="public_profile"),
    path('like-post/', views.like_post, name="like_post"),

]
