from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile
from django.contrib import messages
from . import forms, models, mixins
import requests
import os

# request, "rooms/search.html", {"form": form, "rooms": rooms}
# Create your views here.
class LoginView(mixins.LoggedOutOnlyView, FormView):
    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")
    inital = {"email": "msw1302@gmail.com"}

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            pass
        else:
            return reverse("core:home")


def log_out(request):
    messages.info(request, f"See you later {request.user.first_name}")
    logout(request)
    return redirect(reverse("core:home"))


class SignupView(mixins.LoggedOutOnlyView, FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret_key=key)
        user.email_verified = True
        user.email_secret_key = ""
        user.save()
    except models.User.DoesNotExist:
        # to do :add error message
        pass
    return redirect(reverse("core:home"))


def github_login(self):
    client_id = os.environ.get("GH_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
    )


def github_callback(request):
    try:
        code = request.GET.get("code", None)
        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        if code is not None:
            result = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            result_json = result.json()
            error = result_json.get("error", None)
            if error is not None:
                raise GithubException("Can't get access token")
            else:
                access_token = result_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    bio = profile_json.get("bio")
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method == models.User.LOGIN_GITHUB:
                            # trying to log in
                            pass
                        else:
                            raise GithubException(
                                f"Please log in with: {user.login_method}"
                            )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            username=email,
                            email=email,
                            first_name=name,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Can't get your profile")

        else:
            raise GithubException("Can't get code")
    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def kakao_login(request):
    REST_API_KEY = os.environ.get("KKO_KEY")
    print(REST_API_KEY)
    REDIRECT_URI = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code"
    )


def kakao_callback(request):
    try:
        code = request.GET.get("code")
        REST_API_KEY = os.environ.get("KKO_KEY")
        REDIRECT_URI = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&code={code}&redirect_uri={REDIRECT_URI}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("Can't get authorization code.")
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()
        kakao_account = profile_json.get("kakao_account")
        properties = profile_json.get("properties")
        email = kakao_account.get("email")
        if email is None:
            raise KakaoException("Please also give me your email")
        nickname = properties.get("nickname")
        thumbnail_image = properties.get("profile_image")
        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException(f"Please log in with: {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
                email_verified=True,
            )
            user.set_unusable_password()
            user.save()
            if thumbnail_image is not None:
                photo_request = requests.get(thumbnail_image)
                user.avatar.save(
                    f"{nickname}-avatar", ContentFile(photo_request.content)
                )
                messages.success(request, f"Welcome back {user.first_name}")
        login(request, user)
        return redirect(reverse("core:home"))

    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class KakaoException(Exception):
    pass


class GithubException(Exception):
    pass


class UserProfileView(DetailView):
    model = models.User
    context_object_name = "user_obj"


class UpdateUserView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "email",
        "first_name",
        "last_name",
        "avatar",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency",
    )
    success_message = "Profile Updated"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["birthdate"].widget.attrs = {"placeholder": "BirthDate"}
        form.fields["first_name"].widget.attrs = {"placeholder": "First Name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last Name"}
        form.fields["email"].widget.attrs = {"placeholder": "Email"}
        form.fields["gender"].widget.attrs = {"placeholder": "Sex"}
        return form

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        self.object.username = email
        self.object.save()
        return super().form_valid(form)


class UpdatePasswordView(
    mixins.EmailLoginOnlyView,
    mixins.LoggedInOnlyView,
    SuccessMessageMixin,
    PasswordChangeView,
):
    template_name = "users/update_password.html"
    success_message = "Password Update"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Current Password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New Password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "Confirm New Password"
        }
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()