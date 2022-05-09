from rest_framework.test import APITestCase
from rest_framework import status

from pos_log.models import PosLog
from restaurants.models import Group, Restaurant
from menu.models import Menu
import datetime

def Date(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d').date()

#미리 정의하지 않는다면 Django가 자동으로 {default 세팅에 작성한 이름}_test 로 테스트용 데이터베이스를 생성함
'''
작성자 : 남기윤
Reviewer: 하정현
'''
class PosLogTestCase(APITestCase):
    
    def setUp(self):
        #테스트 그룹 생성
        self.group_data = Group.objects.create(
            group_name = '테스트그룹'
        )
        self.not_group_data = Group.objects.create(
            group_name = 'not테스트그룹'
        )
        #테스트 점포 생성
        self.restaurant1_data = Restaurant.objects.create(
            restaurant_name = "테스트점포1",
            group_id = self.group_data.id,
            city = "테스트도시1",
            address = "테스트지역주소1"
        )
        self.restaurant2_data = Restaurant.objects.create(
            restaurant_name = "테스트점포2",
            group_id = self.group_data.id,
            city = "테스트도시2",
            address = "테스트지역주소2"
        )
        self.not_restaurant_data = Restaurant.objects.create(
            restaurant_name = "not테스트점포",
            group_id = self.not_group_data.id,
            city = "not테스트도시",
            address = "not테스트지역주소"
        )
        #테스트 메뉴 생성
        self.menu_data = Menu.objects.create(
            group_id = self.group_data.id,
            menu_name = "테스트메뉴",
            price = 200000,
        )
        #테스트용 poslog데이터 생성
        p = PosLog.objects.create(
            price = 1000,
            number_of_party = 2,
            payment = "CARD",
            restaurant_id = self.restaurant1_data.id,
        )
        p.timestamp = Date("2022-02-01")
        p.save()
        #correct
        p = PosLog.objects.create(
            price = 10000,
            number_of_party = 3,
            payment = "CARD",
            restaurant_id = self.restaurant2_data.id,
        )
        p.timestamp = Date("2022-02-02")
        p.save()
        #correct
        p = PosLog.objects.create(
            price = 100002,
            number_of_party = 3,
            payment = "CARD",
            restaurant_id = self.restaurant1_data.id,
        ) #not correct (가격)
        p.timestamp = Date("2022-02-02")
        p.save()
        p = PosLog.objects.create(
            price = 10003,
            number_of_party = 5,
            payment = "CARD",
            restaurant_id = self.restaurant1_data.id,
        ) #not correct (인원)
        p.timestamp = Date("2022-02-02")
        p.save()
        p = PosLog.objects.create(
            price = 10004,
            number_of_party = 3,
            payment = "CARD",
            restaurant_id = self.not_restaurant_data.id,
        ) #not correct (그룹)
        p.timestamp = Date("2022-02-02")
        p.save()

    def test_correct_create(self): #정상적으로 생성됐을 때
        data = {
            "restaurant" : self.restaurant1_data.id,
            "price" : 100000,
            "number_of_party" : 1,
            "payment" : "CASH",
            "menu_list" : [
                {
                    "menu":self.menu_data.id,
                    "count":1
                },
                {
                    "menu": self.menu_data.id,
                    "count":3
                }
            ]
        }
        create_response = self.client.post('/api/pos', data=data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

    def test_correct_post_nomal(self):
        data = [
            {
                "date": "2022-02-01",
                "restaurant_id": self.restaurant1_data.id,
                "total_price": 1000,
                'number_of_party': 2,
                'count': 1,
            },
            {
                "date": "2022-02-02",
                "restaurant_id": self.restaurant2_data.id,
                "total_price": 10000,
                'number_of_party': 3,
                'count': 1,
            }
        ]
        response = self.client.get(f"/api/pos?start-time=2022-02-01&end-time=2022-02-02&timesize=day&min-price=100&max-price=50000&group={self.group_data.id}&min-party=2&max-party=3")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.json(), data)