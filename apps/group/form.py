from django import forms
from .models import Group
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'students']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        if instance:
            self.fields['students'].queryset = User.objects.filter(
                role='student'
            ).filter(
                models.Q(student_groups=None) | models.Q(student_groups=instance)
            )
        else:
            self.fields['students'].queryset = User.objects.filter(
                role='student',
                student_groups=None
            )