from django.db.models import Q, Sum, F
from django.db.models.functions import TruncHour, TruncDay, TruncWeek, TruncMonth, TruncYear

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
        group = request.GET.get('group')
        start_time = request.GET.get('start-time')
        end_time = request.GET.get('end-time', start_time)
        timesize = request.GET.get('timesize', None)
        address = request.GET.get('address')

        q = Q()
        if group:
            q &= Q(restaurant__group = group)
        if start_time:
            if start_time > end_time:
                return Response({"message" : "날짜를 다시 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
            q &= Q(timestamp__range = [f'{start_time} 00:00:00', f'{end_time} 23:59:59'])
        if address:
            q &= Q(restaurant__address__icontains = address)

        if timesize is None:
            return Response({"message" : "timezise를 설정해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        time_form = {
            'hour' : TruncHour('timestamp'),
            "day" : TruncDay('timestamp'),
            "week" : TruncWeek('timestamp'),
            "month" : TruncMonth('timestamp'),
            "year" : TruncYear('timestamp')
            }

        data = (PosLog.objects.filter(q)
        .annotate(date = time_form[timesize])
        .values('date')
        .annotate(total_price = Sum('price'))
        .values('date', 'total_price')
        )
        return Response(list(data))


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
