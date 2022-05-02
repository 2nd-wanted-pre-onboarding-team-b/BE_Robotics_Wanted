from django.db import models

from restaurants.models import Restaurant
from menu.models import Menu

class PosLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    price = models.IntegerField()
    number_of_party = models.IntegerField()
    payment = models.CharField(max_length=50)
    menu = models.ManyToManyField(Menu, related_name='menu')

    class Meta:
        db_table = 'pos_log'