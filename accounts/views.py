from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from .forms import AddUserForm, EditUserForm
from django.views.decorators.http import require_http_methods


def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name="Admin").exists()
    )


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"


@login_required
def home(request):
    if is_admin(request.user):
        return render(request, "accounts/dashboard.html")

    return redirect("public-map")


@login_required
def user_list(request):
    if not is_admin(request.user):
        raise PermissionDenied

    User = get_user_model()
    users = User.objects.prefetch_related("groups").order_by("username")

    rows = []

    for account in users:
        groups = {group.name for group in account.groups.all()}

        if account.is_superuser or "Admin" in groups:
            role = "Admin"
        elif "User" in groups:
            role = "User"
        elif "Viewer" in groups:
            role = "Viewer"
        else:
            role = "Not assigned"

        rows.append({
            "account": account,
            "role": role,
        })

    return render(
        request,
        "accounts/user_list.html",
        {"rows": rows},
    )

@login_required
def user_add(request):
    if not is_admin(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = AddUserForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("accounts:user_list")
    else:
        form = AddUserForm()

    return render(
        request,
        "accounts/user_form.html",
        {"form": form},
    )


@login_required
def user_edit(request, user_id):
    if not is_admin(request.user):
        raise PermissionDenied

    User = get_user_model()
    account = get_object_or_404(User, pk=user_id)

    if account.is_superuser and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        form = EditUserForm(
            request.POST,
            instance=account,
            actor=request.user,
        )

        if form.is_valid():
            updated_user = form.save()

            if updated_user.pk == request.user.pk:
                update_session_auth_hash(request, updated_user)

            return redirect("accounts:user_list")
    else:
        form = EditUserForm(
            instance=account,
            actor=request.user,
        )

    return render(
        request,
        "accounts/user_edit.html",
        {
            "form": form,
            "account": account,
        },
    )

@login_required
@require_http_methods(["GET", "POST"])
def user_delete(request, user_id):
    if not is_admin(request.user):
        raise PermissionDenied

    User = get_user_model()
    account = get_object_or_404(User, pk=user_id)

    blocked_reason = ""

    if account.pk == request.user.pk:
        blocked_reason = "You cannot delete your own account."
    elif account.is_superuser:
        blocked_reason = (
            "Superuser accounts cannot be deleted from this page."
        )

    if request.method == "POST" and not blocked_reason:
        account.delete()
        return redirect("accounts:user_list")

    return render(
        request,
        "accounts/user_confirm_delete.html",
        {
            "account": account,
            "blocked_reason": blocked_reason,
        },
        status=403 if blocked_reason else 200,
    )