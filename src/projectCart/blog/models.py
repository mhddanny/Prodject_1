from django.db import models
from profiles.models import Account
from django.core.validators import FileExtensionValidator
# Create your models here.

class Post(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    intro = models.TextField()
    body = models.TextField()
    image = models.ImageField(upload_to='photos/posts', blank=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])], default='images/default.png')
    created_add = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_add']