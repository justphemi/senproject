import io

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from PIL import Image

from .models import Profile
from .forms import ProfileForm, UsernameLookupForm


def make_image(name="test.png", fmt="PNG", size=(10, 10), color=(255, 0, 0), file_size=None):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color)
    img.save(buf, format=fmt)
    data = buf.getvalue()
    if file_size:
        data = data + b" " * (file_size - len(data))
    return SimpleUploadedFile(name, data, content_type=f"image/{fmt.lower()}")


class ProfileModelTests(TestCase):
    def test_create_profile(self):
        user = User.objects.create(username="alice")
        p = Profile.objects.create(user=user, display_name="Alice")
        self.assertEqual(str(p), "Alice")
        self.assertEqual(p.user.username, "alice")

    def test_display_name_required(self):
        user = User.objects.create(username="bob")
        profile = Profile(user=user, display_name="")
        with self.assertRaises(ValidationError):
            profile.full_clean()


class ProfileFormTests(TestCase):
    def test_display_name_required(self):
        form = ProfileForm(data={"display_name": "", "bio": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("display_name", form.errors)

    def test_valid_form(self):
        form = ProfileForm(data={"display_name": "Alice", "bio": "hello"})
        self.assertTrue(form.is_valid())

    def test_avatar_type_rejects_gif(self):
        gif = make_image("pic.gif", fmt="GIF")
        form = ProfileForm(
            data={"display_name": "Alice"},
            files={"avatar": gif},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("avatar", form.errors)

    def test_avatar_size_limit(self):
        big = make_image("big.png", fmt="PNG", file_size=2 * 1024 * 1024)
        form = ProfileForm(
            data={"display_name": "Alice"},
            files={"avatar": big},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("avatar", form.errors)

    def test_jpg_accepted(self):
        jpg = make_image("pic.jpg", fmt="JPEG")
        form = ProfileForm(
            data={"display_name": "Alice"},
            files={"avatar": jpg},
        )
        self.assertTrue(form.is_valid())


class UsernameLookupFormTests(TestCase):
    def test_blank_rejected(self):
        form = UsernameLookupForm(data={"username": ""})
        self.assertFalse(form.is_valid())

    def test_valid(self):
        form = UsernameLookupForm(data={"username": "alice_01"})
        self.assertTrue(form.is_valid())


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_get(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)

    def test_lookup_creates_user(self):
        r = self.client.post(reverse("home"), {"username": "newuser"})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(Profile.objects.filter(user__username="newuser").exists())

    def test_lookup_existing_user(self):
        User.objects.create(username="existing")
        r = self.client.post(reverse("home"), {"username": "existing"})
        self.assertEqual(r.status_code, 302)

    def test_profile_view(self):
        r = self.client.get(reverse("profile_view", args=["someone"]))
        self.assertEqual(r.status_code, 200)

    def test_edit_get(self):
        r = self.client.get(reverse("profile_edit", args=["someone"]))
        self.assertEqual(r.status_code, 200)

    def test_edit_post_valid(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (10, 10), (255, 0, 0)).save(buf, format="JPEG")
        jpg = SimpleUploadedFile("a.jpg", buf.getvalue(), content_type="image/jpeg")
        r = self.client.post(
            reverse("profile_edit", args=["someone"]),
            data={"display_name": "Updated", "bio": "new bio", "avatar": jpg},
        )
        self.assertEqual(r.status_code, 302)
        profile = Profile.objects.get(user__username="someone")
        self.assertEqual(profile.display_name, "Updated")
        self.assertTrue(bool(profile.avatar))

    def test_edit_post_empty_name_rejected(self):
        r = self.client.post(
            reverse("profile_edit", args=["someone"]),
            data={"display_name": "", "bio": ""},
        )
        self.assertEqual(r.status_code, 200)


class EditorModalTests(TestCase):
    def test_edit_page_renders_avatar_trigger(self):
        r = self.client.get(reverse("profile_edit", args=["carol"]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="avatarWrap"')
        self.assertContains(r, 'id="editorModal"')
        self.assertContains(r, 'id="brightnessRange"')
        self.assertContains(r, 'data-filter="bw"')
        self.assertContains(r, 'data-filter="bright_up"')
        self.assertContains(r, 'data-filter="bright_down"')

    def test_edit_page_renders_modal_close_buttons(self):
        r = self.client.get(reverse("profile_edit", args=["carol"]))
        self.assertContains(r, 'id="modalClose"')
        self.assertContains(r, 'id="modalCancel"')
        self.assertContains(r, 'id="modalDone"')

    def test_edit_save_final_image_redirects(self):
        buf = io.BytesIO()
        Image.new("RGB", (40, 40), (200, 100, 50)).save(buf, format="JPEG")
        jpg = SimpleUploadedFile("final.jpg", buf.getvalue(), content_type="image/jpeg")
        r = self.client.post(
            reverse("profile_edit", args=["dave"]),
            data={"display_name": "Dave", "bio": "hello", "avatar": jpg},
        )
        self.assertEqual(r.status_code, 302)
        profile = Profile.objects.get(user__username="dave")
        self.assertEqual(profile.display_name, "Dave")
        self.assertEqual(profile.bio, "hello")
        self.assertTrue(bool(profile.avatar))
