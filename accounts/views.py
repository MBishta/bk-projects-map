from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"


@login_required
def home(request):
    return redirect("public-map")