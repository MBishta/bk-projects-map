from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.db import transaction


User = get_user_model()


def get_role_choices():
    return [
        ("", "Select a role"),
        *[
            (name, name)
            for name in Group.objects.order_by("name").values_list(
                "name", flat=True
            )
        ],
    ]


class AddUserForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
    )

    role = forms.ChoiceField(
        choices=[],
        label="Role",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
            "password1",
            "password2",
        )
        labels = {
            "username": "Username",
            "first_name": "First Name",
            "last_name": "Last Name",
            "is_active": "Active account",
        }
        help_texts = {
            "is_active": "Inactive users cannot sign in.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = get_role_choices()

        if Group.objects.filter(name="Viewer").exists():
            self.fields["role"].initial = "Viewer"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email

    def clean_role(self):
        role = self.cleaned_data["role"]

        if not Group.objects.filter(name=role).exists():
            raise forms.ValidationError(
                "This role is not configured. Please contact the administrator."
            )

        return role

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)

        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()
            self.save_m2m()
            user.groups.set([
                Group.objects.get(name=self.cleaned_data["role"])
            ])

        return user


class EditUserForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
    )

    role = forms.ChoiceField(
        choices=[],
        label="Role",
    )

    new_password1 = forms.CharField(
        required=False,
        label="New Password",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password"}
        ),
        help_text="Leave blank to keep the current password.",
    )

    new_password2 = forms.CharField(
        required=False,
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
        )
        labels = {
            "username": "Username",
            "first_name": "First Name",
            "last_name": "Last Name",
            "is_active": "Active account",
        }

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        self.fields["role"].choices = get_role_choices()

        groups = list(
            self.instance.groups.order_by("name").values_list(
                "name", flat=True
            )
        )

        if "Admin" in groups:
            current_role = "Admin"
        elif "User" in groups:
            current_role = "User"
        elif "Viewer" in groups:
            current_role = "Viewer"
        else:
            current_role = groups[0] if groups else ""

        self.initial["role"] = current_role

        self.protect_access = (
            self.instance.pk == actor.pk
            or self.instance.is_superuser
        )

        if self.protect_access:
            self.fields["role"].disabled = True
            self.fields["role"].required = False
            self.fields["is_active"].disabled = True

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        duplicate = User.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk)

        if duplicate.exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email

    def clean_role(self):
        role = self.cleaned_data.get("role", "")

        if self.protect_access:
            return role

        if not Group.objects.filter(name=role).exists():
            raise forms.ValidationError(
                "This role is not configured."
            )

        return role

    def clean(self):
        cleaned = super().clean()

        actor_is_admin = (
            self.actor.is_authenticated
            and self.actor.is_active
            and (
                self.actor.is_superuser
                or self.actor.groups.filter(name="Admin").exists()
            )
        )

        if not actor_is_admin:
            raise forms.ValidationError(
                "Only administrators can edit users."
            )

        if self.instance.is_superuser and not self.actor.is_superuser:
            raise forms.ValidationError(
                "You cannot edit this administrator account."
            )

        password1 = cleaned.get("new_password1", "")
        password2 = cleaned.get("new_password2", "")

        if password1 != password2:
            self.add_error(
                "new_password2",
                "The passwords do not match.",
            )

        return cleaned

    def _post_clean(self):
        super()._post_clean()

        password = self.cleaned_data.get("new_password1")

        if password:
            try:
                validate_password(password, self.instance)
            except forms.ValidationError as errors:
                self.add_error("new_password1", errors)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("new_password1")

        if password:
            user.set_password(password)

        if commit:
            user.save()

            if not self.protect_access:
                user.groups.set([
                    Group.objects.get(
                        name=self.cleaned_data["role"]
                    )
                ])

        return user