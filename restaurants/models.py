from django.db import models

from model_utils.models import TimeStampedModel

class Group(TimeStampedModel):
    group_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.group_name

    class Meta:
        db_table = 'groups'
        indexes = [
            models.Index(fields=('group_name',),  name='group_name_idx')
        ]

class Restaurant(TimeStampedModel):
    restaurant_name = models.CharField(max_length=50)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    address = models.TextField()

    def __str__(self):
        return self.restaurant_name

    class Meta:
        db_table = 'restaurants'
        indexes = [
            models.Index(fields=('restaurant_name',), name='restaurant_name_idx'),
            models.Index(fields=('city',), name='city_idx'),
        ]