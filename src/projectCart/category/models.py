from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from mptt.models import MPTTModel, TreeForeignKey
import uuid

class Category(MPTTModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/category', blank=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])], default='images/default.png')
    video_file = models.FileField(upload_to='videos/category', blank=True, validators=[FileExtensionValidator(allowed_extensions=['mp4'])])
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_publish = models.BooleanField(default=False)

    class MPTTMeta:
        order_insertion_by = ['category_name']

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name

    def delete(self):
        self.cat_image.delete()
        self.video_file.delete()
        super().delete()
