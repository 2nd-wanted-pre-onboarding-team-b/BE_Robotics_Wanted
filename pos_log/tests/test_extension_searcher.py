from rest_framework.test import APITestCase
from rest_framework import status
from menu.models import *
from pos_log.models import *
from restaurants.models import *
from django.db import connection

import csv
import json

"""
Writer: 하정현

인원/결제수단 집계함수 테스트 코드
"""
def load_data(i_root):
    """
    테스트 돌리기 전, DB에 테스트용 데이터 업로드
    """
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

class TestExtensionSearcher(APITestCase):

    API         = "/api/pos2"

    @classmethod
    def setUpTestData(cls):
        # 테스트 전 DB에 테스트 할 데이터 업로드
        load_data("pos_log/tests/inputs/expanded_searcher")

    def test_omit_nessary(self):
        """
        필수 부분 빠져있는 것에 대한 예외 처리
        """

        # omit start time
        req = {"end-time": "2022-04-07", "timesize": "HOUR"}
        self.assertEqual(
            self.client.get(self.API, req).status_code, 406)

        # omit end time
        req = {"start-time": "2022-04-07", "timesize": "HOUR"}
        self.assertEqual(
            self.client.get(self.API, req).status_code, 406)

        # omit timesize
        req = {"start-time": "2022-04-07", "end-time": "2022-04-07"}
        self.assertEqual(
            self.client.get(self.API, req).status_code, 406)

    
    def test_payment_all_day(self):

        req = {
            "start-time"    : "2022-01-10",
            "end-time"      : "2023-05-25",
            "timesize"      : "day",
            "payment"       : "all"
        }
        answer = [
            {"restaurant_id": 1, "payment": "BITCOIN", "count": 1, "date": "2022-02-23"},
            {"restaurant_id": 1, "payment": "CARD", "count": 2, "date": "2022-02-23"},
            {"restaurant_id": 1, "payment": "CASH", "count": 1, "date": "2023-04-22"},
            {"restaurant_id": 2, "payment": "PHONE", "count": 1, "date": "2022-02-23"},
            {"restaurant_id": 2, "payment": "CASH", "count": 1, "date": "2022-02-24"},
            {"restaurant_id": 3, "payment": "CASH", "count": 1, "date": "2022-02-24"},
            {"restaurant_id": 3, "payment": "BITCOIN", "count": 1, "date": "2022-03-13"}
        ]
        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)

    def test_payment_card_day(self):

        req = {
            "start-time"    : "2022-01-10",
            "end-time"      : "2023-05-25",
            "timesize"      : "day",
            "payment"       : "CARD"
        }
        answer = [
            {"restaurant_id": 1, "payment": "CARD", "count": 2, "date": "2022-02-23"}
        ]
        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)

    def test_numofparty_all_day(self):
        
        req = {
            "start-time": "2022-01-10",
            "end-time": "2023-05-25",
            "timesize": "day",
            "number-of-party": "all"
        }
        answer = [
            {"restaurant_id": 1, "number_of_party": 3, "count": 3, "date": "2022-02-23"},
            {"restaurant_id": 2, "number_of_party": 1, "count": 1, "date": "2022-02-23"},
            {"restaurant_id": 3, "number_of_party": 1, "count": 1, "date": "2022-02-24"},
            {"restaurant_id": 2, "number_of_party": 2, "count": 1, "date": "2022-02-24"},
            {"restaurant_id": 3, "number_of_party": 4, "count": 1, "date": "2022-03-13"},
            {"restaurant_id": 1, "number_of_party": 2, "count": 1, "date": "2023-04-22"}
        ]
        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)