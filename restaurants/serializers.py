from rest_framework import serializers
from restaurants.models import *

class RestaurantSerializer(serializers.ModelSerializer):
    """
    작성자: 하정현
    RestaurantSerializer
    """
    # Date 포맷은 YYYY-MM-DD HH-MM-SS
    created = serializers.DateTimeField(required=False, format='%Y-%m-%d %H:%M:%S')
    modified = serializers.DateTimeField(required=False, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        fields = '__all__'
        read_only_fields = ('created', 'modified', 'id')
        model = Restaurant

    def validate(self, data):
        # timestamp 맘대로 지정/수정 불가
        NO_MODIFIED = {'created', 'modified'}
        for k in NO_MODIFIED:
            if k in data:
                raise serializers.ValidationError(f"No {k} modified")
        return data