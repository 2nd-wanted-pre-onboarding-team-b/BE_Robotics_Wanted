from typing import Optional, Sequence, Dict, Set, List
from datetime import datetime
from pos_log.models import PosLog
from pos_log.modules.extension_searcher_validator import *
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth, TruncYear, TruncHour, TruncWeek

from restaurants.models import Restaurant

class ExtensionLogSearcher:

    """
        Writer: 하정현
        Pos Log데이터를 이용한 확장 분석 메소드가 있는
        클래스
    """
    
    @staticmethod
    @sb_payment_validator
    def search_by_payment(
        time_range  : Sequence[datetime],
        time_size   : str,
        price_range : Optional[Sequence[int]] = None,
        party_size  : Optional[Sequence[int]] = None,
        restaurant_group    : Optional[str] = None
    ) -> List[Dict[str, object]]:
        """
            결제수단 집계 함수

            param:
                time_range          : 시간 범위 (start, end)
                time_size           : HOUR, DAY, WEEK, MONTH, YEAR
                price_range         : 가격 범위 (min price, max price) [선택]
                party_size          : 결제 하나 당 인원 수 [선택]
                restaurant_group    : 식당 프랜차이즈 [선택]

            return:
                Dict 형태의 결과값
                Validate 실패 시 ValueError 호출
                필요한 param 없을 시 TypeError 호출

            input data에 대한 검증은 sb_payment_validator에서 진행했으므로
            바로 집계 작업에 들어간다.

            Call SQL Statement by ORM
            1. filter timestamp
            2. set value
            3. OPTIONAL FILTERLING
                3.1. filter price range
                3.2. filter party size
                3.3. filter restaurant_group
            4. group record by time_size
            5. sorting: 'restaurant_id' -> 'date' -> 'payment'
        """

        result: List[Dict[str, object]] = []
        __result: object = None
        
        # 1. filter timestamp
        time_range[0] = time_range[0].date()
        time_range[1] = time_range[1].date()
        __result = PosLog.objects.filter(
            timestamp__gte=time_range[0], 
            timestamp__lte=time_range[1])

        # 2. set value
        __result = __result.values('restaurant_id', 'payment')

        # 3. OPTIONAL FILTERING
        if price_range:
            __result = __result.filter(
                price__gte=price_range[0], 
                price__lte=price_range[1])
        if party_size:
            __result = __result.filter(
                number_of_party__gte=party_size[0],
                number_of_party__lte=party_size[1])
        if restaurant_group:
            __result = __result.filter(restaurant__restaurant_name=restaurant_group)

        # 4. group record by time_size
        TIME_SIZE_MAP: Dict[str, object] = {
            "DAY": TruncDate('timestamp'),
            "MONTH": TruncMonth('timestamp'),
            "YEAR": TruncYear('timestamp'),
            "HOUR": TruncHour('timestamp'),
            "WEEK": TruncWeek('timestamp')
        }
        __result = __result.annotate(count=Count('payment'), date=TIME_SIZE_MAP[time_size])

        # 5. sorting
        if __result:
            # 결과가 있을 때만 한다.
            result = __result.order_by('restaurant_id', 'date', 'payment')

        return result

    @staticmethod
    @sb_partysize_validator
    def search_by_party(
        time_range  : Sequence[datetime],
        time_size   : str,
        price_range : Optional[Sequence[int]] = None,
        party_size  : Optional[Sequence[int]] = None,
        restaurant_group    : Optional[str] = None
    ) -> List[Dict[str, object]]:
        """
            인원 집계 함수

            param:
                time_range          : 시간 범위 (start, end)
                time_size           : HOUR, DAY, WEEK, MONTH, YEAR
                price_range         : 가격 범위 (min price, max price) [선택]
                party_size          : 결제 하나 당 인원 수 [선택]
                restaurant_group    : 식당 프랜차이즈 [선택]

            return:
                Dict 형태의 결과값
                Validate 실패 시 ValueError 호출
                필요한 param 없을 시 TypeError 호출

            input data에 대한 검증은 sb_partysize_validator에서 진행했으므로
            바로 집계 작업에 들어간다.
            
            Call SQL Statement by ORM
            1. filter timestamp
            2. set value
            3. OPTIONAL FILTERLING
                3.1. filter price range
                3.2. filter party size
                3.3. filter restaurant_group
            4. group record by number_of_party
            5. sorting: 'restaurant_id' -> 'date' -> '-number_of_party'
        """

        # Call SQL Statement by ORM
        result: List[Dict[str, object]] = []
        __result: object = None

        # 1. filter timestamp
        time_range[0] = time_range[0].date()
        time_range[1] = time_range[1].date()
        __result = PosLog.objects.filter(
            timestamp__gte=time_range[0], 
            timestamp__lte=time_range[1])
        
        # 2. set value
        __result = __result.values('restaurant_id', 'number_of_party')

        # 3. OPTIONAL FILTERING
        if price_range:
            __result = __result.filter(
                price__gte=price_range[0], 
                price__lte=price_range[1])
        if party_size:
            __result = __result.filter(
                number_of_party__gte=party_size[0],
                number_of_party__lte=party_size[1])
        if restaurant_group:
            __result = __result.filter(restaurant__restaurant_name=restaurant_group)

        # 4. group record by time_size
        TIME_SIZE_MAP: Dict[str, object] = {
            "DAY": TruncDate('timestamp'),
            "MONTH": TruncMonth('timestamp'),
            "YEAR": TruncYear('timestamp'),
            "HOUR": TruncHour('timestamp'),
            "WEEK": TruncWeek('timestamp')
        }
        __result = __result.annotate(count=Count('number_of_party'), date=TIME_SIZE_MAP[time_size])

        # 5. sorting
        if __result:
            # 결과가 있을 때만 한다.
            result = __result.order_by('restaurant_id', 'date', '-number_of_party')
        return result