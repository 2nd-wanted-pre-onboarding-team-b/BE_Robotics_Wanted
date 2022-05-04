from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import PosLog, PosLogMenu
from menu.models import Menu
from .serializers import PosLogSerializer

from django.db.models import Q, F, Sum, Count
from django.db.models.functions import  TruncWeek, TruncDate, ExtractHour, ExtractMonth, ExtractYear

import datetime

def Date(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d').date()

class PoslogListView(APIView):
    '''
    작성자 : 남기윤
    (POST) /api/pos - pos_log CREATE API
    (GET) /api/pos? - 기간(필수),timesize(필수),가격,인원,그룹,정보를 받아 검색하는 API
    '''

class PosLogSearchView(APIView):
    '''
    확장 검색 API
    (GET) /api/pos2
    '''
    def post(self, request):
        '''
        작성자: 남기윤
        '''
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

    def get(self, request):
        '''
        작성자:하정현, 남기윤
        '''
        """ CONST VALUES """
        TIME_FORM = {
            'hour'  : ExtractHour('timestamp'),
            'day'   : TruncDate('timestamp'),
            'week'  : TruncWeek('timestamp'),
            'month' : ExtractMonth('timestamp'),
            'year'  : ExtractYear('timestamp')
        }

        """ PARAMS """
        start_time  = request.GET.get("start-time")
        end_time    = request.GET.get("end-time")
        timesize    = request.GET.get("timesize")
        min_price   = request.GET.get("min-price")
        max_price   = request.GET.get("max-price")
        min_party   = request.GET.get("min-party")
        max_party   = request.GET.get("max-party")
        group       = request.GET.get("group")
        payment     = request.GET.get("payment")
        num_of_party= request.GET.get("number-of-party")

        # 하나라도 없으면 안됨
        if not all((start_time, end_time, timesize)):
            return Response(status = status.HTTP_406_NOT_ACCEPTABLE)
        # timesize validate
        if timesize not in {'day', 'hour', 'week', 'month', 'year'}:
            return Response(status = status.HTTP_406_NOT_ACCEPTABLE)
        
        q = Q()
        q &= Q(timestamp__gte=Date(start_time))
        q &= Q(timestamp__lte=Date(end_time)+datetime.timedelta(days=1))

        if min_price:
            q &= Q(price__gte=min_price)
        if max_price:
            q &= Q(price__lte=max_price)
        if min_party:
            q &= Q(number_of_party__gte=min_party)
        if max_party:
            q &= Q(number_of_party__lte=max_party)
        if group:
            q &= Q(restaurant__group_id=group)

        res = PosLog.objects.filter(q).annotate(date=TIME_FORM[timesize]).values('date')

        if payment:
            # 결제수단 기준
            res = res.annotate(count=Count('payment'))
            if payment != 'all':
                res = res.filter(payment=payment)
            res = res.values('restaurant_id', 'count', "payment", "date")
        elif num_of_party:
            # 인원 기준
            res = res.annotate(count=Count('number_of_party'))
            if num_of_party != 'all':
                res = res.filter(number_of_party=num_of_party)
            res = res.values('restaurant_id', 'count', "number_of_party", "date")
        else:
            res = res.annotate(
            time = TIME_FORM[timesize]
        ).values('time').annotate(
            restaurant_id = F('restaurant'),
            total_price = Sum('price')
        ).values('time', 'restaurant_id', 'total_price')

        return Response(res, status=status.HTTP_200_OK)