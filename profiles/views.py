from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import ProfileForm, UsernameLookupForm
from .models import Profile


def home(request):
    form = UsernameLookupForm()
    if request.method == "POST":
        form = UsernameLookupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            user, created = User.objects.get_or_create(username=username)
            if created:
                Profile.objects.create(user=user, display_name=username)
            return redirect("profile_view", username=user.username)
    return render(request, "profiles/home.html", {"form": form})


def profile_view(request, username):
    user, _ = User.objects.get_or_create(username=username)
    profile, _ = Profile.objects.get_or_create(user=user, defaults={"display_name": username})
    return render(request, "profiles/profile_view.html", {"profile": profile, "page_user": user})


def profile_edit(request, username):
    user, _ = User.objects.get_or_create(username=username)
    profile, _ = Profile.objects.get_or_create(user=user, defaults={"display_name": username})

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile_view", username=user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "profiles/profile_edit.html",
        {"form": form, "profile": profile, "page_user": user},
    )