from pos_log.models import *
from menu.models import *
from restaurants.models import *

from pos_log.tests.tools.converter import str2datetime
from pos_log.tests.tools.customed_api_testcase import CustomedAPITestCase
from pos_log.tests.tools.runner import test_runner
from pos_log.modules.extension_searcher import ExtensionLogSearcher
from pos_log.tests.tools.converter import str2datetime
from typing import Dict, List
from django.db import connection
import csv

def check_validate(c: CustomedAPITestCase, time_range, time_size,
    price_range, party_size, restaurant_group):

    if time_range:
        # str을 datetime으로 변형
        for i in range(len(time_range)):
            time_range[i] = str2datetime(time_range[i])
    try:
        # 테스트 실행
        ExtensionLogSearcher.search_by_payment(
            time_range          = time_range, 
            time_size           = time_size, 
            price_range         = price_range,
            party_size          = party_size, 
            restaurant_group    = restaurant_group)
    except (ValueError, TypeError) as e:
        return False
    except Exception as e:
        raise e
    else:
        return True

def check_result(c: CustomedAPITestCase, time_range, time_size,
    price_range, party_size, restaurant_group):
    if time_range:
        # str을 datetime으로 변형
        for i in range(len(time_range)):
            time_range[i] = str2datetime(time_range[i])
    try:
        res: List[Dict[str, object]] = ExtensionLogSearcher.search_by_payment(
            time_range          = time_range, 
            time_size           = time_size, 
            price_range         = price_range,
            party_size          = party_size, 
            restaurant_group    = restaurant_group)
    except Exception as e:
        return [f"ERROR {e}"]
    else:
        # 테스트 판정을 위한 데이터 가공
        KEY2INDEX_MAP: Dict[str, int] = {
            "date"          : 0,
            "restaurant_id" : 1,
            "payment"       : 2,
            "count"         : 3
        }
        res4test: List[Dict[str, object]] = []
        for r in res:
            record4test: List[object] = [None] * 4
            for k,v in r.items():
                if k == 'date':
                    if time_size == 'DAY' or time_size == 'WEEK':
                        v = f"{v.year}-{v.month}-{v.day}"
                    elif time_size == 'HOUR':
                        v = f"{v.hour}"
                    elif time_size == 'MONTH':
                        v = f"{v.month}"
                    elif time_size == 'YEAR':
                        v = f"{v.year}"
                record4test[KEY2INDEX_MAP[k]] = v
            res4test.append(record4test)
        return res4test

class TestExtensionSearcherByPayment(CustomedAPITestCase):

    """
        Writer: 하정현

        인원 집계함수 테스트 코드
    """
    input_root: str = "pos_log/tests/inputs/query_expanded"
    input_files: Dict[str, str] = {
            "test_validate": "query_search_payment_failed_params.json",
            "test_result": "query_search_payment_result.json"
    }

    @classmethod
    def setUpTestData(cls):
        i_root = TestExtensionSearcherByPayment.input_root

        # Group 생성
        with open(f"{i_root}/test_group.csv", "rt") as f:
            reader = csv.reader(f)
            for g_name in reader:
                if g_name == 'group_name':
                    continue
                g = Group(group_name = g_name)
                g.save()

        # 식당 생성
        with open(f"{i_root}/test_res.csv", "rt") as f:
            reader = csv.reader(f)
            
            for gi, n, c, a in reader:
                if gi == 'group_id':
                    continue
                r = Restaurant(
                    group=Group.objects.get(id=int(gi)),
                    restaurant_name=n,
                    city=c,
                    address=a
                )
                r.save()

        # Log 생성
        with open(f"{i_root}/test_log.csv", 'rt') as f:
            reader = csv.reader(f)
            i = 1
            for t, ri, p, nop, pay in reader:
                if t == 'timestamp':
                    continue
                
                # id 자동생성 문제로 인하여 Raw Query로 해결
                with connection.cursor() as cursor:
                    s = f"INSERT INTO pos_log VALUES ({i},'{t}',{p},{nop},'{pay}',{ri})"
                    cursor.execute(s)
                i += 1
    
    @test_runner(test_func=check_validate)
    def test_validate(self):
        pass

    @test_runner(test_func=check_result)
    def test_result(self):
        pass