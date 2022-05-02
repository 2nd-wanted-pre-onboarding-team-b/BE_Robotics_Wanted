from django.db import models

from model_utils.models import TimeStampedModel

from restaurants.models import Group


class Menu(TimeStampedModel):
    menu_name = models.CharField(max_length=50)
    price = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.menu_name

    class Meta:
        db_table = 'menu'
        indexes = [
            models.Index(fields=('menu_name',), name='menu_name_idx')
        ]