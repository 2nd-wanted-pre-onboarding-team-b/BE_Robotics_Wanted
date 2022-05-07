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
    (GET) /api/pos - pos_log LIST ALL
    (POST) /api/pos - pos_log CREATE API
    (GET) /api/pos? - 기간(필수),timesize(필수),가격,인원,그룹,정보를 받아 검색하는 API
    '''
    def get(self, request):
        data = PosLog.objects.all()
        serializer = PosLogGetSerializer(data, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PoslogDetailView(APIView): 
    '''
    작성자 : 남기윤
    (GET) /api/pos<int:id> - pos_log SHOWS TARGET
    (PATCH) /api/pos<int:id> - pos_log UPDATES TARGET
    (DELETE) /api/pos<int:id> - pos_log DELETES TARGET
    '''
    def get(self, request, pos_id):
        pos_log = get_object_or_404(PosLog, pk=pos_id)
        serializer = PosLogGetSerializer(pos_log)
        return Response(serializer.data)

    def patch(self, request, pos_id):
        data = request.data
        pos_log = get_object_or_404(PosLog, pk=pos_id)
        serializer = PosLogSerializer(pos_log, data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            target_log = PosLog.objects.get(id=serializer.data['id'])
            for i in data['menu_list']:
                data = PosLogMenu(pos_log=target_log, menu=Menu.objects.get(id=i['menu']), count=i['count'])
                data.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pos_id): 
        pos_log = get_object_or_404(PosLog, pk=pos_id)
        pos_log.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PosLogSearchView(APIView):
    '''
    확장 검색 API
    (GET) /api/pos/search
    '''


    def get(self, request):
        """
        작성자 : 하정현, 남기윤, 최승리
        """
        restaurant = request.GET.get('restaurant')
        group = request.GET.get('group')
        start_time = request.GET.get('start-time')
        end_time = request.GET.get('end-time', start_time)
        end_time = request.GET.get('end-time', None)
        timesize = request.GET.get('timesize', None)
        address = request.GET.get('address')
        min_price = request.GET.get("min-price")
        max_price = request.GET.get("max-price", None)
        min_party = request.GET.get("min-party")
        max_party = request.GET.get("max-party", None)
        payment = request.GET.get("payment")
        group_by = request.GET.get("group-by", None)

        q = Q()
        # 과도한 쿼리가 작동하는 것을 방지하기 위해 시간범위는 필수 지정
        if not all((start_time, end_time, timesize)) or timesize not in {'day', 'hour', 'week', 'month', 'year'}:
            return Response({"message": "start_time, end_time, timesize 필수데이터를 확인하세요"}, status = status.HTTP_400_BAD_REQUEST)

        if restaurant:
            q &= Q(restaurant = restaurant)

        if group:
            q &= Q(restaurant__group = group)

        if start_time:
            if start_time > end_time:
                return Response({"message" : "날짜를 다시 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
            q &= Q(timestamp__range = [f'{start_time} 00:00:00', f'{end_time} 23:59:59'])

        if address:
            q &= Q(restaurant__address__icontains = address)

        if min_price:
            if max_price is None:
                return Response({"message" : "가격을 다시 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
            q &= Q(price__range = [min_price, max_price])

        if min_party:
            if max_party is None:
                return Response({"message" : "인원을 다시 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
            q &= Q(number_of_party__range = [min_party, max_party])

        if payment:
            payment = payment.split(',')
            q &= Q(payment__in = payment)

        time_form = {
            'hour' : ExtractHour('timestamp'),
            "day" : TruncDate('timestamp'),
            "week" : TruncWeek('timestamp'),
            "month" : ExtractMonth('timestamp'),
            "year" : ExtractYear('timestamp')
            }

        base_query = PosLog.objects.filter(q).annotate(date = time_form[timesize]).values('date')

        if payment:
            base_query = (
                base_query
                .annotate(count = Count('id'))
                .values('restaurant_id', 'payment', 'date', 'count')
                )
        elif min_party:
            base_query = (
                base_query
                .annotate(count = Count('id'), total_price = Sum('price'))
                .values('restaurant_id', 'number_of_party', 'date', 'count', 'total_price')
                )
        elif address or group_by:
            base_query = (
                base_query
                .annotate(total_price = Sum('price'))
                .values("date", 'total_price')
                )
        else:
            base_query = (
                base_query
                .annotate(restaurant_id = F('restaurant'), total_price = Sum('price'))
                .values('restaurant_id', 'date', 'total_price')
                )
        return Response(base_query, status=status.HTTP_200_OK)