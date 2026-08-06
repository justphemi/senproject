import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_avatar_size(image):
    max_size_mb = 1
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f"Image too large. Max size is {max_size_mb} MB."
        )


def validate_avatar_type(image):
    allowed = ["JPEG", "PNG"]
    fmt = getattr(image, "image", None)
    actual = getattr(fmt, "format", None) if fmt else None
    if actual is None:
        name = (image.name or "").lower()
        if name.endswith(".jpg") or name.endswith(".jpeg"):
            actual = "JPEG"
        elif name.endswith(".png"):
            actual = "PNG"
    if actual not in allowed:
        raise ValidationError(
            "Unsupported image type. Only JPG and PNG are allowed."
        )


def avatar_upload_path(instance, filename):
    username = instance.user.username if instance.user_id else "anon"
    ext = os.path.splitext(filename or "")[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png"):
        ext = ".jpg"
    return f"avatars/{username}/{uuid.uuid4().hex}{ext}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=60)
    bio = models.TextField(blank=True, max_length=300)
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        validators=[validate_avatar_size, validate_avatar_type],
    )
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        errors = {}
        if not (self.display_name or "").strip():
            errors["display_name"] = "Display name is required."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.display_name or self.user.username