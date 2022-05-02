from django.contrib import admin

from .models import PosLog


@admin.register(PosLog)
class PosLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'restaurant', 'price', 'number_of_party', 'payment',)
    filter_horizontal = ('menu',)
    search_fields = ('restaurant__restaurant_name',)