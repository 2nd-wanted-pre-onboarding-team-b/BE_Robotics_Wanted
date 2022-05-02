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
