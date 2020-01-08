from django.db import models

# Create your models here.
class Orders(models.Model):
    openid = models.CharField(max_length=56, blank=True)
    order_id = models.CharField(max_length=36)
    item_title = models.CharField(max_length=70)

