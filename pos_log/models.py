from django.db import models

from restaurants.models import Restaurant
from menu.models import Menu

class PosLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    price = models.IntegerField()
    number_of_party = models.IntegerField()
    payment = models.CharField(max_length=50)
    menu = models.ManyToManyField(Menu, related_name='menu', through='PosLogMenu')

    class Meta:
        db_table = 'pos_log'

class PosLogMenu(models.Model):
    pos_log = models.ForeignKey(PosLog, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
    count = models.IntegerField()

    class Meta:
        db_table = 'pos_log_menu'
