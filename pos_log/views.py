from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import PosLog, PosLogMenu
from menu.models import Menu
from .serializers import PosLogSerializer
from restaurants.models import Restaurant

from django.db.models import Q, F, Sum, Count
from django.db.models.functions import TruncHour, TruncDay, TruncMonth, TruncWeek, TruncYear, TruncDate
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

class PosLogSearcherView(APIView):
    '''
    Writer: 하정현
    
    확장 검색 API
    (GET) /api/pos/<search_type:str>
    '''
    def get(self, request, search_type):
        """
            search_type: payment: 결제수단에 대한 검색
            search_type: number-of-party: 영수증 하나 당 인원 수에 대한 검색
        """
        from pos_log.modules.lambdas import Inputs, Validators, Filters

        """ ERRORS """
        err_406 = lambda: Response(status = status.HTTP_406_NOT_ACCEPTABLE)
        err_400 = lambda: Response(status = status.HTTP_400_BAD_REQUEST)
        err_200 = lambda res: Response(res, status = status.HTTP_200_OK)
        """
        Lambda FUNCTIONS
        
        func: url2column:   number of party일 경우 search_type에 "-"를 "_"로 변경된 결로 출력
        func: str2datetime: string to datetime
        func: is_omited:    쿼리 작동에 필요한 요소들이 있는 지 확인. True일 경우 Failed
        """
        url2column      = lambda s: "number_of_party" if s == "number-of-party" else s
        str2datetime    = lambda s: datetime.datetime.strptime(s, "%Y-%m-%d")
        is_omited       = lambda t_start, t_end, t_size : not all([t_start, t_end, t_size])

        if search_type not in {"payment", "number-of-party"}:
            # payment, partysize 아니면 400 처리
            return err_400()

        # Param 받기
        # res_group은 restaurant_group의 줄임말이다.
        time_range, timesize, price_range, party_range, res_group = \
            Inputs.search_log(request.GET)

        # 필수 사항
        # 얘네들 없으면 안됨
        if is_omited(*time_range, timesize):
            return err_406()

        # Timesize 대문자 처리
        timesize = timesize.upper() if timesize else None

        try:
            # str상태인 범위 인자를 상황에 맞게 변형
            time_range = list(map(str2datetime, time_range))

            to_int = lambda e: int(e) if e != None else None
            price_range = list(map(to_int, price_range))
            party_range = list(map(to_int, party_range))
        except Exception:
            return err_406()

        # 파리미터에 대한 예외 처리
        is_passed = Validators.Searcher.res_group(          \
            Validators.Searcher.party_size(                 \
                Validators.Searcher.price_range(            \
                    Validators.Searcher.time_size(          \
                        Validators.Searcher.time_range(     \
                            True                            \
                        ,*time_range)                       \
                    ,timesize)                              \
                ,*price_range)                              \
            ,*party_range)                                  \
        ,res_group)

        if not is_passed:
            # 통과 못하면 에러
            return err_406()

        # 필터 생성
        q = Filters.Searcher.restaurant_group(      \
            Filters.Searcher.party(                 \
                Filters.Searcher.price(             \
                    Filters.Searcher.timestamp(     \
                        Q()                         \
                    ,*time_range)                   \
                ,*price_range)                      \
            ,*party_range)                          \
        ,res_group)

        # 필터를 이용한 PosLog 조회
        result = PosLog.objects.filter(q).values("restaurant_id")

        # Timesize에 대한 Table
        generate_timesize_table = lambda count_col: \
        {
            "DAY":      ["date", lambda q: q.annotate(
                                count=Count(count_col), date=TruncDate('timestamp'))],
            "MONTH":    ["month", lambda q: q.annotate(
                                count=Count(count_col), month=TruncMonth('timestamp'))],
            "YEAR":     ["year", lambda q: q.annotate(
                                count=Count(count_col), year=TruncYear('timestamp'))],
            "HOUR":     ["hour", lambda q: q.annotate(
                                count=Count(count_col), hour=TruncHour('timestamp'))],
            "WEEK":     ["week", lambda q: q.annotate(
                                count=Count(count_col), week=TruncWeek('timestamp'))]
        }
        TIME_SIZE_TRUNC = generate_timesize_table(url2column(search_type))

        # 결재 수단, 또는 인원 수로 Count 묶기
        result = TIME_SIZE_TRUNC[timesize][1](result).values(   \
            'restaurant_id', 'count', url2column(search_type), TIME_SIZE_TRUNC[timesize][0])

        """
        TODO: testsize에 대해 date format을 다르게 해야 하는데
        원래는 쿼리단에서 이를 해결해야 성능이 빠르나 계속되는 오류로
        임시방편으로 쿼리 작업 후 반복문에서 진행

        예를 들어 HOUR이면 2022-08-01 8:43:00에 시간만 빼서 8로 변환한다.
        key값이 date에서 hour로 바뀌어 date: 8에서 hour: 8로 바뀐다.
        """
        zp = lambda x: str(x).zfill(2)
        TIME_SIZE_FORMAT = {
            "HOUR"  : lambda x: f"{x.hour}",
            "DAY"   : lambda x: f"{x.year}-{zp(x.month)}-{zp(x.day)}",
            "YEAR"  : lambda x: f"{x.year}",
            "MONTH" : lambda x: f"{x.month}",
            "WEEK"  : lambda x: f"{x.year}-{zp(x.month)}-{zp(x.day)}"
        }
        for i in range(len(result)):
            k = 'date' if timesize == 'DAY' else timesize.lower()
            result[i][k] = TIME_SIZE_FORMAT[timesize](result[i][k])
        return err_200(result)