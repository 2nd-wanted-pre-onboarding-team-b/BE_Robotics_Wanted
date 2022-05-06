from rest_framework import serializers
from .models import  PosLog, PosLogMenu
import json

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
    
    menu = serializers.SerializerMethodField()
    
    
    class Meta:
        model = PosLog
        fields = (
            "id","timestamp","restaurant","price","number_of_party","payment",
            "menu",
            )
    
    def get_menu(self, obj): 
        data = PosLogMenu.objects.filter(pos_log = obj.id)
        res = []
        for i in data:
            res.append(
                {'menu_name':i.menu.menu_name,
                'count':i.count
                })
        return res