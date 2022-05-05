from django.db.models import Q, Sum, F, Count
from django.db.models.functions import TruncDay, TruncWeek, ExtractHour, ExtractMonth, ExtractYear

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .models import Menu
from .serializers import MenuSerializer

from pos_log.models import PosLog


class MenuViewSet(ModelViewSet):
    serializer_class = MenuSerializer
    queryset = Menu.objects.all()


class BonusPointView(APIView):
    def get(self, request):
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
            "day" : TruncDay('timestamp'),
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
        elif address:
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


class MenuSalesView(APIView):
    """
    작성자 : 최승리
    """
    def get(self, request):
        start_time = request.GET.get('start-time')
        end_time = request.GET.get('end-time', start_time)
        menu_list = request.GET.get('menu-list', None)
        order = request.GET.get('order', '-total_price')

        try:
            menu_list = list(map(lambda x : int(x), menu_list.split(',')))
        except (ValueError, AttributeError):
            return Response({"error_message" : "메뉴를 다시 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)

        q = Q()
        if menu_list:
            q &= Q(poslogmenu__menu__in = menu_list)
        if start_time:
            if start_time > end_time:
                return Response({"error_message" : "날짜를 다시 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
            q &= Q(timestamp__range = [f'{start_time} 00:00:00', f'{end_time} 23:59:59'])

        data = (PosLog.objects
        .filter(q)
        .values('poslogmenu__menu')
        .annotate(
            total_price = Sum('poslogmenu__count') * F('poslogmenu__menu__price'),
            menu_name = F('poslogmenu__menu__menu_name')
            )
        .order_by(order)
        )

        return Response(list(data), status=status.HTTP_200_OK)
