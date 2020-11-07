from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from . import forms
from . import models
import requests
import os

# request, "rooms/search.html", {"form": form, "rooms": rooms}
# Create your views here.
class LoginView(FormView):
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


def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))


class SignupView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    initial = {
        "first_name": "Min",
        "last_name": "JeongHoo",
        "email": "msw1302@gmail.com",
    }

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
                raise GithubException()
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
                            raise GithubException()
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
                    raise GithubException()

        else:
            raise GithubException()
    except GithubException:
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
            raise KakaoException()
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
            raise KakaoException()
        nickname = properties.get("nickname")
        thumbnail_image = properties.get("profile_image")
        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException()
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
        login(request, user)
        return redirect(reverse("core:home"))

    except KakaoException:
        return redirect(reverse("users:login"))


class KakaoException(Exception):
    pass


class GithubException(Exception):
    pass
