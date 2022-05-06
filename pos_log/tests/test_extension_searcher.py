from rest_framework.test import APITestCase
from rest_framework import status
from menu.models import *
from pos_log.models import *
from restaurants.models import *
from django.db import connection

"""
Writer: 하정현

인원/결제수단 집계함수 테스트 코드
"""
def load_data(groups, restuarants, logs):
    """
    테스트 돌리기 전, DB에 테스트용 데이터 업로드
    """
    # Group 생성
    for g_name in groups:
        if g_name == 'group_name':
            continue
        g = Group(group_name = g_name)
        g.save()

    # 식당 생성
    for gi, n, c, a in restuarants:
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
    i = 1
    for t, ri, p, nop, pay in logs:
        if t == 'timestamp':
            continue

        with connection.cursor() as cursor:
            s = f"INSERT INTO pos_log VALUES ({i},'{t}',{p},{nop},'{pay}',{ri})"
            cursor.execute(s)
        i += 1

class TestExtensionSearcher(APITestCase):

    API = "/api/pos"

    @classmethod
    def setUpTestData(cls):
        # 테스트 전 DB에 테스트 할 데이터 업로드
        groups = ['g1', 'g2', 'g3', 'g4', 'g5']
        restaurants = [
            ['1','res_a1','city2','address1'],
            ['1','res_b2','city1','address1'],
            ['2','res_c1','city3','address1'],
            ['3','res_c2','city3','address1'],
            ['4','res_d2','city3','address1'],
            ['5','res_e1','city1','address1'],
        ]
        logs = [
            # 날짜, 식당 아이디, 금액, numbers of party, 수단
            ['2022-02-23 13:05:00','1','3000','3','CARD'],
            ['2022-02-23 13:15:00','1','3000','3','CARD'],
            ['2022-02-23 13:58:00','2','4000','1','PHONE'],
            ['2022-02-23 16:42:00','1','3000','3','BITCOIN'],
            ['2022-02-24 06:00:00','2','5000','2','CASH'],
            ['2022-02-24 09:23:00','3','3000','1','CASH'],
            ['2022-02-25 13:15:00','1','3000','3','CARD'],
            ['2022-03-13 10:43:00','3','4000','4','BITCOIN'],
            ['2023-04-22 20:44:00','1','3000','2','CASH']
        ]
        load_data(groups, restaurants, logs)

    def test_omit_nessary(self):
        """
        필수 부분 빠져있는 것에 대한 예외 처리
        """

        # omit start time
        req = {"end-time": "2022-04-07", "timesize": "hour"}
        self.assertEqual(
            self.client.get(self.API, req).status_code, 400)

        # omit end time
        req = {"start-time": "2022-04-07", "timesize": "hour"}
        self.assertEqual(
            self.client.get(self.API, req).status_code, 400)

        # omit timesize
        req = {"start-time": "2022-04-07", "end-time": "2022-04-07"}
        self.assertEqual(
            self.client.get(self.API, req).status_code, 400)

    def test_wrong_nessesary_params(self):
        """
        알맞지않은 파라미터
        """

        req = {
            "start-time"    : "2022-04-05",
            "end-date"      : "???",
            "timesize"      : "hour"
        }
        self.assertEqual(
            self.client.get(self.API, req).status_code, 400,
            msg="end date의 데이터가 알맞지 않음")

        # 이상한 timesize
        req['end-date'] = '2022-05-01'
        req['timesize'] = 'mayday'
        self.assertEqual(
            self.client.get(self.API, req).status_code, 400,
            msg="엉뚱한 timesize")

        req = {
            "start-time"    : "2022-04-05",
            "end-date"      : "2022-05-01",
            "timesize"      : 3478392
        }
        self.assertEqual(
            self.client.get(self.API, req).status_code, 400,
            msg="tiemsize가 정수형임")
        

        req = {
            "start-time"    : "2022-04-",
            "end-date"      : "2022-05-01",
            "timesize"      : "hour"
        }
        self.assertEqual(
            self.client.get(self.API, req).status_code, 400,
            msg="timeformat 상태가 안좋음")

        req = {
            "start-time"    : "2022-04-35",
            "end-date"      : "2022-05-41",
            "timesize"      : "hour"
        }
        self.assertEqual(
            self.client.get(self.API, req).status_code, 400,
            msg="datetime 수치가 비정상")

        req = {
            "start-time"    : "2022-04-05",
            "end-date"      : "2022-04-04",
            "timesize"      : "hour"
        }
        self.assertEqual(
            self.client.get(self.API, req).status_code, 400,
            msg="start date가 앞서있음")


    def test_payment_all_day(self):

        req = {
            "start-time"    : "2022-01-10",
            "end-time"      : "2023-04-22",
            "timesize"      : "day",
            "payment"       : "CARD,BITCOIN,CASH,PHONE"
        }
        answer = [
            {"restaurant_id": 1, "payment": "BITCOIN", "count": 1, "date": "2022-02-23"},
            {"restaurant_id": 1, "payment": "CARD", "count": 2, "date": "2022-02-23"},
            {"restaurant_id": 1, "payment": "CASH", "count": 1, "date": "2023-04-22"},
            {"restaurant_id": 2, "payment": "PHONE", "count": 1, "date": "2022-02-23"},
            {"restaurant_id": 2, "payment": "CASH", "count": 1, "date": "2022-02-24"},
            {"restaurant_id": 3, "payment": "CASH", "count": 1, "date": "2022-02-24"},
            {"restaurant_id": 1, "payment": "CARD", "count": 1, "date": "2022-02-25"},
            {"restaurant_id": 3, "payment": "BITCOIN", "count": 1, "date": "2022-03-13"}
        ]

        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)

    def test_payment_all_hour(self):
        req = {
            "start-time"    : "2022-01-10",
            "end-time"      : "2023-05-25",
            "timesize"      : "hour",
            "payment"       : "CARD,BITCOIN,CASH,PHONE" 
        }
        answer = [
            {"restaurant_id": 1, "payment": "CARD", "count": 3, "date": 13},
            {"restaurant_id": 1, "payment": "BITCOIN", "count": 1, "date": 16},
            {"restaurant_id": 1, "payment": "CASH", "count": 1, "date": 20},
            {"restaurant_id": 2, "payment": "PHONE", "count": 1, "date": 13},
            {"restaurant_id": 2, "payment": "CASH", "count": 1, "date": 6},
            {"restaurant_id": 3, "payment": "CASH", "count": 1, "date": 9},
            {"restaurant_id": 3, "payment": "BITCOIN", "count": 1, "date": 10}
        ]
        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)

    def test_payment_all_year(self):
        req = {
            "start-time"    : "2022-01-10",
            "end-time"      : "2023-05-25",
            "timesize"      : "year",
            "payment"       : "CARD,BITCOIN,CASH,PHONE"
        }
        answer = [
            {"restaurant_id": 1, "payment": "BITCOIN", "count": 1, "date": 2022},
            {"restaurant_id": 1, "payment": "CARD", "count": 3, "date": 2022},
            {"restaurant_id": 1, "payment": "CASH", "count": 1, "date": 2023},
            {"restaurant_id": 2, "payment": "CASH", "count": 1, "date": 2022},
            {"restaurant_id": 2, "payment": "PHONE", "count": 1, "date": 2022},
            {"restaurant_id": 3, "payment": "BITCOIN", "count": 1, "date": 2022},
            {"restaurant_id": 3, "payment": "CASH", "count": 1, "date": 2022}
        ]
        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)


    def test_payment_all_short_year(self):
        """ 범위를 2023으로 좁힘
        """
        req = {
            "start-time"    : "2023-03-10",
            "end-time"      : "2023-05-25",
            "timesize"      : "year",
            "payment"       : "CARD,BITCOIN,CASH,PHONE"
        }
        answer = [
            {"restaurant_id": 1, "payment": "CASH", "count": 1, "date": 2023}
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
            {"restaurant_id": 1, "payment": "CARD", "count": 2, "date": "2022-02-23"},
            {"restaurant_id": 1, "payment": "CARD", "count": 1, "date": "2022-02-25"}
        ]
        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)

    def test_numofparty_all_day(self):
        req = {
            "start-time"    : "2022-01-10",
            "end-time"      : "2023-05-25",
            "timesize"      : "day",
            "min-party"     : 1,
            "max-party"     : 10,
            "number-of-party": "CARD,BITCOIN,CASH,PHONE"
        }
        answer = [
            {"restaurant_id": 1, "number_of_party": 3, "count": 3, "date": "2022-02-23", 'total_price': 9000},
            {"restaurant_id": 2, "number_of_party": 1, "count": 1, "date": "2022-02-23", 'total_price': 4000},
            {"restaurant_id": 3, "number_of_party": 1, "count": 1, "date": "2022-02-24", 'total_price': 3000},
            {"restaurant_id": 2, "number_of_party": 2, "count": 1, "date": "2022-02-24", 'total_price': 5000},
            {"restaurant_id": 3, "number_of_party": 4, "count": 1, "date": "2022-03-13", 'total_price': 4000},
            {"restaurant_id": 1, "number_of_party": 2, "count": 1, "date": "2023-04-22", 'total_price': 3000},
            {'restaurant_id': 1, 'number_of_party': 3, 'count': 1, 'date': '2022-02-25', 'total_price': 3000}
        ]

        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)

    def test_numofparty_all_hour(self):
        req = {
            "start-time"    : "2022-01-10",
            "end-time"      : "2023-05-25",
            "timesize"      : "hour",
            "min-party"     : 1,
            "max-party"     : 10,
            "number-of-party": "CARD,BITCOIN,CASH,PHONE"
        }
        answer = [
            {"restaurant_id": 1, "number_of_party": 3, "count": 3, "date": 13, 'total_price': 9000},
            {"restaurant_id": 2, "number_of_party": 1, "count": 1, "date": 13, 'total_price': 4000},
            {"restaurant_id": 1, "number_of_party": 3, "count": 1, "date": 16, 'total_price': 3000},
            {"restaurant_id": 2, "number_of_party": 2, "count": 1, "date": 6, 'total_price': 5000},
            {"restaurant_id": 3, "number_of_party": 1, "count": 1, "date": 9, 'total_price': 3000},
            {"restaurant_id": 3, "number_of_party": 4, "count": 1, "date": 10, 'total_price': 4000},
            {"restaurant_id": 1, "number_of_party": 2, "count": 1, "date": 20, 'total_price': 3000}
        ]
        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)


    def test_numofparty_all_year(self):
        req = {
            "start-time"    : "2022-01-10",
            "end-time"      : "2023-05-25",
            "timesize"      : "year",
            "min-party"     : 1,
            "max-party"     : 10,
            "number-of-party": "CARD,BITCOIN,CASH,PHONE"
        }
        answer = [
            {"restaurant_id": 1, "number_of_party": 3, "count": 4, "date": 2022, 'total_price': 12000},
            {"restaurant_id": 2, "number_of_party": 1, "count": 1, "date": 2022, 'total_price': 4000},
            {"restaurant_id": 2, "number_of_party": 2, "count": 1, "date": 2022, 'total_price': 5000},
            {"restaurant_id": 3, "number_of_party": 4, "count": 1, "date": 2022, 'total_price': 4000},
            {"restaurant_id": 3, "number_of_party": 1, "count": 1, "date": 2022, 'total_price': 3000},
            {"restaurant_id": 1, "number_of_party": 2, "count": 1, "date": 2023, 'total_price': 3000}
        ]
        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)


    def test_numofparty_all_month(self):
        req = {
            "start-time"    : "2022-01-10",
            "end-time"      : "2023-05-25",
            "timesize"      : "month",
            "min-party"     : 1,
            "max-party"     : 10,
            "number-of-party": "CARD,BITCOIN,CASH,PHONE"
        }
        answer = [
            {"restaurant_id": 1, "number_of_party": 3, "count": 4, "date": 2, 'total_price': 12000},
            {"restaurant_id": 2, "number_of_party": 1, "count": 1, "date": 2, 'total_price': 4000},
            {"restaurant_id": 2, "number_of_party": 2, "count": 1, "date": 2, 'total_price': 5000},
            {"restaurant_id": 3, "number_of_party": 1, "count": 1, "date": 2, 'total_price': 3000},
            {"restaurant_id": 3, "number_of_party": 4, "count": 1, "date": 3, 'total_price': 4000},
            {"restaurant_id": 1, "number_of_party": 2, "count": 1, "date": 4, 'total_price': 3000}
        ]
        res = self.client.get(self.API, req)
        self.assertEqual(res.status_code, 200)
        self.assertCountEqual(res.json(), answer)