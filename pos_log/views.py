
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import PosLog, PosLogMenu
from menu.models import Menu
from .serializers import PosLogSerializer
from restaurants.models import Restaurant

from django.db.models import Q, F, Sum
from django.db.models.functions import TruncHour, TruncDay, TruncMonth, TruncWeek, TruncYear
import datetime

def Date(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d').date()

class PoslogListView(APIView):
    '''
    작성자 : 남기윤
    (POST) /api/pos
    
    input eg.
    {
    "restaurant" : 21,
    "price" : 5000,
    "number_of_party" : 1,
    "payment" : "CASH",
    "menu_list" : [
        {
            "menu":2,
            "count":1
        },
        {
            "menu":1,
            "count":3
        }
    ]
    }

    (GET) /api/pos?
    '''

    def post(self, request):
        data = request.data
        serializer = PosLogSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            target_log = PosLog.objects.get(id=serializer.data['id'])
            for i in data['menu_list']:
                data = PosLogMenu(pos_log=target_log, menu=Menu.objects.get(id=i['menu']), count=i['count'])
                data.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        try:
            start_time = request.GET.get("start-time")
            end_time = request.GET.get("end-time")
            timesize = request.GET.get("timezise")
            q = Q()
            q &= Q(timestamp__gte=Date(start_time))
            q &= Q(timestamp__lte=Date(end_time))
        except:
            return Response(status = status.HTTP_406_NOT_ACCEPTABLE)
        
        min_price = request.GET.get("min-price",None)
        max_price = request.GET.get("max-price",None)
        min_party = request.GET.get("min-party",None)
        max_party = request.GET.get("max-party",None)
        group = request.GET.get("group",None)
        
        
        if min_price:
            q &= Q(price__gte=min_price)
        if max_price:
            q &= Q(price__lte=max_price)
        if min_party:
            q &= Q(number_of_party__gte=min_party)
        if max_party:
            q &= Q(number_of_party__lte=max_party)
        if group:
            
            restaurant_group = Restaurant.objects.filter(Q(group_id = group)).values('id')

            q &= Q(restaurant__in=restaurant_group)

            pos_data = PosLog.objects.filter(q).values()
        
        time_form = {
            'hour' :TruncHour('timestamp'),
            'day':TruncDay('timestamp'),
            'week':TruncWeek('timestamp'),
            'month':TruncMonth('timestamp'),
            'year':TruncYear('timestamp'),
        }
        pos_data = pos_data.annotate(
            date = time_form[timesize]
        ).values('date').annotate(
            restaurant_id = F('restaurant'),
            total_price = Sum('price')
        ).values('date', 'restaurant_id', 'total_price')
        
        return Response(pos_data, status=status.HTTP_201_CREATED)
