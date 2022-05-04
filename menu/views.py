from datetime import datetime, timedelta
from sqlite3 import Timestamp

from django.db.models import Q, Sum, F
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics

from .models import Menu
from .serializers import MenuSerializer

from pos_log.models import PosLog


class MenuListView(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class MenuDetailView(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class BonusPointView(APIView):
    def get(self, request):
        group = request.GET.get('group')
        start_time = request.GET.get('start-time')
        end_time = request.GET.get('end-time')
        timesize = request.GET.get('timesize')
        address = request.GET.get('address')

        q = Q()
        if group:
            q &= Q(restaurant__group = group)
        if start_time:
            q &= Q(timestamp__range = [start_time, datetime.strptime(end_time, '%Y-%m-%d')+timedelta(days=1)])
        if address:
            q &= Q(restaurant__address__icontains = address)

        time_form = {
            "day" : TruncDay('timestamp'),
            "week" : TruncWeek('timestamp'),
            "month" : TruncMonth('timestamp'),
            "year" : TruncYear('timestamp')
            }

        data = (PosLog.objects.filter(q)
        .annotate(date = time_form[f'{timesize}'])
        .values('date')
        .annotate(total_price = Sum('price'))
        .values('date', 'total_price')
        )
        return Response(list(data))

class BonusPointMenuView(APIView):
    def get(self, request):
        start_time = request.GET.get('start-time')
        end_time = request.GET.get('end-time')
        menu_01 = request.GET.get('menu-01')
        menu_02 = request.GET.get('menu-02')

        q = Q()
        q1 = Q(poslogmenu__menu = menu_01)
        q2 = Q(poslogmenu__menu = menu_02)

        if start_time:
            q = Q(timestamp__range = [start_time, datetime.strptime(end_time, '%Y-%m-%d') + timedelta(days = 1)])

        data = (PosLog.objects
        .filter((q1 | q2), q)
        .values('poslogmenu__menu')
        .annotate(total_price = Sum('price'), menu_name = F('poslogmenu__menu__menu_name'))
        )

        return Response(list(data))
