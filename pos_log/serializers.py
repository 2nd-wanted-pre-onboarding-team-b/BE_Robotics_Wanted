from django.db.models import F

from rest_framework import serializers
from .models import  PosLog

class PosLogSerializer(serializers.ModelSerializer):
    '''
    작성자 : 남기윤
    '''
    class Meta:
        model = PosLog
        fields = (
            "id","timestamp","restaurant","price","number_of_party","payment",
            "menu",
            )

class  PosLogGetSerializer(serializers.ModelSerializer):
    '''
    작성자 : 남기윤
    '''
    menu = serializers.SerializerMethodField()

    class Meta:
        model = PosLog
        fields = (
            "id","timestamp","restaurant","price","number_of_party","payment",
            "menu",
            )

    def get_menu(self, obj): 
        menu_data = (obj.poslogmenu_set
        .annotate(menu_name=F('menu__menu_name'))
        .values('menu_name', 'count')
        )
        return menu_data
