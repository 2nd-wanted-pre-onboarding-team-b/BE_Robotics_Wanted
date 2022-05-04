from django.db.models import Q

"""
Writer: 하정현

쿼리 작업에 사용되는 람다 조각들
"""

# x가 존재하면 True, 존재하지 않으면 False
f = lambda x: x is not None

class Inputs:
    """
        GET 파라미터를 받는 람다식
    """
    search_log = lambda rget: [
        [rget.get("start-time"), rget.get("end-time")],
        rget.get("timesize"),
        [rget.get("min-price"), rget.get("max-price")],
        [rget.get("min-party"), rget.get("max-party")],
        rget.get("group")
    ]
class Validators:
    """
    특정 Input값에 대한 예외 처리 모음
    전부 static function이므로 클래스를 선언해서 쓸 필요가 없다.
    """
    class Searcher:
        """
        검색 관련 Input값 예외 처리 함수
        
        True: 통과, False: 실패

        설명:
            "l":    현재 예외 처리 여부의 상태이며 True는 아직 통과된 상황이고,
                    False는 이미 이전에 통과되지 않는 경우이다.
                    "l"이 앞에 있으므로 False이면 뒤의 논리식 검사도 수행하지 않는다.

            time_range:     시작 시간이 끝 시간 보다 늦으면 안된다.
            time_size:      time_size는 HOUR, DAY, WEEK, MONTH, YEAR중에 하나만 있어야 한다.
                            (단, API단에서 timesize는 대문자로 치환하고 작업하기 때문에, 대소문자 판별은 하지 않는다.)
            price_range:    선택 사항이므로 min, max 두개 다 없어도 통과된다.
                            두개 다 있을 경우 min이 max보다 크면 안되며
                            하나만 있고 나머지 하나가 None이면 통과하지 못한다.
            party_size:     price_range와 동일한 논리식
            res_group:      제약 사항 없음
        """
        TIME_SIZE   = {'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'}
        time_range  = lambda l, s, e:   l & (s <= e)
        time_size   = lambda l, t:      l & (t in Validators.Searcher.TIME_SIZE)
        price_range = lambda l, s, e:   l & (((not f(s))and(not f(e))) | ((f(s)&f(e))and(0<=s<=e)))
        party_size  = lambda l, s, e:   l & (((not f(s))and(not f(e))) | ((f(s)&f(e))and(0<=s<=e)))
        res_group   = lambda l, g:      l
class Filters:
    """
    Query Filter 생성 함수 모음
    """
    class Searcher:
        """
        검색 관련 필터 조각들
        """
        timestamp   = lambda q, start, end:         \
                        q & Q(timestamp__gte=start, timestamp__lte=end)

        price       = lambda q, start, end:         \
                        q if not start or not end   \
                        else q & Q(price__gte=start, price__lte=end)

        party       = lambda q, start, end:         \
                        q if not start or not end   \
                        else q & Q(number_of_party__gte=start, number_of_party__lte=end)

        restaurant_group    = lambda q, group:      \
                                q if not group      \
                                else q & Q(restaurant__group_id=group)