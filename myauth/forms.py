from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class StaffUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user
