from django.db import models
from store.models import Category

# Create your models here.

class CategoryOffer(models.Model):
    category_name = models.OneToOneField(Category, on_delete=models.CASCADE)
    discount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)

    def __int__(self):
        return self.category_name
