from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from .views import (
    AccountLoginView,
    home,
    user_list,
    user_add,
    user_edit,
    user_delete,
)
 
app_name = "accounts"

urlpatterns = [
    path("", home, name="home"),

    path("users/", user_list, name="user_list"),

    path("users/add/", user_add, name="user_add"),

    path("login/", AccountLoginView.as_view(), name="login"),

    path("users/<int:user_id>/delete/", user_delete, name="user_delete"),

    path("users/<int:user_id>/edit/", user_edit, name="user_edit"),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path(
        "forgot-password/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset_form.html",
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),

    path(
        "forgot-password/sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset-password/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset-password/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]