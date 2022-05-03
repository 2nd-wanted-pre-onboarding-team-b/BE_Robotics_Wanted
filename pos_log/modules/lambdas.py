from django.db.models import Q

class Inputs:
    """
        GET 파라미터로 받는 람다식
    """
    search_log = lambda rget: [
        [rget.get("start-time"), rget.get("end-time")],
        rget.get("timesize"),
        [rget.get("min-price"), rget.get("max-price")],
        [rget.get("min-party"), rget.get("max-party")],
        rget.get("restaurant_group")
    ]
f = lambda x: x is not None
class Validators:
    class Searcher:
        TIME_SIZE   = {'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'}
        time_range  = lambda l, s, e:   l & (s <= e)
        time_size   = lambda l, t:      l & (t in Validators.Searcher.TIME_SIZE)
        price_range = lambda l, s, e:   l & (((not f(s))&(not f(e))) | ((f(s)&f(e)) and (0<=s<=e)))
        party_size  = lambda l, s, e:   l & (((not f(s))&(not f(e))) | ((f(s)&f(e)) and (0<=s<=e)))
        res_group   = lambda l, g:      l
class Filters:
    class Searcher:
        timestamp   = lambda q, start, end:         \
                    q & Q(timestamp__gte=start, timestamp__lte=end)

        price       = lambda q, start, end:         \
                    q if not start or not end       \
                    else q & Q(price__gte=start, price__lte=end)

        party       = lambda q, start, end:         \
                    q if not start or not end       \
                    else q & Q(number_of_party__gte=start, number_of_party__lte=end)

        restaurant_group    = lambda q, group: q if not group else q & Q(restaurant=group)