from django import forms
from PIL import Image

from .models import Profile


ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]
MAX_FILE_MB = 1


class ProfileForm(forms.ModelForm):
    display_name = forms.CharField(
        max_length=60,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Display name"}),
    )
    bio = forms.CharField(
        required=False,
        max_length=300,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Short bio (optional)"}),
    )
    avatar = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ["display_name", "bio", "avatar"]

    def clean_display_name(self):
        name = (self.cleaned_data.get("display_name") or "").strip()
        if not name:
            raise forms.ValidationError("Display name is required.")
        return name

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not avatar:
            return avatar

        content_type = getattr(avatar, "content_type", None)
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise forms.ValidationError("Only JPG and PNG images are allowed.")

        if avatar.size > MAX_FILE_MB * 1024 * 1024:
            raise forms.ValidationError(
                f"Image too large. Max size is {MAX_FILE_MB} MB."
            )
        return avatar


class UsernameLookupForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter a username"}),
    )

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise forms.ValidationError("Username is required.")
        if not all(c.isalnum() or c in "._-" for c in username):
            raise forms.ValidationError(
                "Username can only contain letters, numbers, dots, underscores, and hyphens."
            )
        return username