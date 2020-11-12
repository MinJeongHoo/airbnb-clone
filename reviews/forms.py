from django import forms

from . import models


class CreateReviewForm(forms.ModelForm):
    class Meta:
        accuracy = forms.IntegerField(max_value=5, min_value=1)
        communication = forms.IntegerField(max_value=5, min_value=1)
        value = forms.IntegerField(max_value=5, min_value=1)
        cleanliness = forms.IntegerField(max_value=5, min_value=1)
        location = forms.IntegerField(max_value=5, min_value=1)
        check_in = forms.IntegerField(max_value=5, min_value=1)
        model = models.Review
        fields = (
            "review",
            "accuracy",
            "communication",
            "value",
            "cleanliness",
            "location",
            "check_in",
        )

    def save(self):
        review = super().save(commit=False)
        return review