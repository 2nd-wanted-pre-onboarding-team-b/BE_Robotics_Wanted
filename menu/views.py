from django.db.models import Q, Sum, F

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


class MenuSalesView(APIView):
    '''
    작성자 : 최승리
    '''
    def get(self, request):
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        menu_list = request.GET.get('menu_list', None)
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

        return Response(data, status=status.HTTP_200_OK)
