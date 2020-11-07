from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from django.utils.html import strip_tags
import uuid
from django.template.loader import render_to_string


class User(AbstractUser):

    """Custom User Model"""

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"

    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    )
    LANGUAGE_ENGLISH = "english"
    LANGUAGE_KOREAN = "korean"

    LANGUAGE_CHOICES = ((LANGUAGE_ENGLISH, "English"), (LANGUAGE_KOREAN, "Korean"))

    CURRENCY_USD = "usd"
    CURRENCY_KOR = "kor"

    CURRENCY_CHOICES = ((CURRENCY_USD, "USD"), (CURRENCY_KOR, "KOR"))

    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = "github"
    LOGIN_KAKAO = "kakao"

    LOGIN_CHOICES = (
        (LOGIN_EMAIL, "Email"),
        (LOGIN_GITHUB, "GitHub"),
        (LOGIN_KAKAO, "Kakao"),
    )

    avatar = models.ImageField(upload_to="avatars", blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, blank=True)
    bio = models.TextField(blank=True)
    birthdate = models.DateField(null=True)
    language = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=2, blank=True, default=LANGUAGE_KOREAN
    )
    currency = models.CharField(
        choices=CURRENCY_CHOICES, max_length=3, blank=True, default=CURRENCY_KOR
    )

    superhost = models.BooleanField(default=False)

    email_verified = models.BooleanField(default=False)
    email_secret_key = models.CharField(max_length=120, default="", blank=True)
    login_method = models.CharField(
        max_length=50, choices=LOGIN_CHOICES, default=LOGIN_EMAIL
    )

    def verify_email(self):
        if self.email_verified is False:
            secret = uuid.uuid4().hex[:20]
            self.email_secret_key = secret
            html_message = render_to_string(
                "email/verify_email.html", {"secret": secret}
            )
            send_mail(
                "Verify Aribnb Account",
                strip_tags(html_message),
                settings.EMAIL_FROM,
                [self.email],
                fail_silently=True,
                html_message=html_message,
            )
            self.save()
        return

    def __str__(self):
        return self.username
