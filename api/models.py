from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    purok = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    family_members = models.TextField()
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"
