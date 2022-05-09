from rest_framework.test import APITestCase
from rest_framework import status

from restaurants.models import *
group_id4test = -1

class TestRestaurantCreate(APITestCase):
    API = '/api/restaurants/create'
    GROUP_NAME = 'my-group'

    @classmethod
    def setUpTestData(cls):
        global group_id4test
        __group = Group.objects.create(group_name=TestRestaurantCreate.GROUP_NAME)
        group_id4test = __group.id

    def test_create_no_found_group(self):
        # 해당 group을 못찾음
        req = {
            'group': 1000,
            'city': 'Seoul',
            'restaurant_name': '식당',
            'address': '서초구'
        }
        self.assertEqual(
            self.client.post(self.API, data=req).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_do_not_create_timestamp(self):
        # timestamp 맘대로 지정 불가
        req = {
            'group': group_id4test,
            'city': 'Seoul',
            'restaurant_name': '식당',
            'address': '서초구',
            'created': '2022-10-10 10:10:10',
            'modified': '2022-10-10 10:10:10'
        }
        self.assertEqual(
            self.client.post(self.API, data=req).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_create_success(self):
        req = {
            'group': group_id4test,
            'city': 'Seoul',
            'restaurant_name': '식당',
            'address': '서초구'
        }
        self.assertEqual(
            self.client.post(self.API, data=req).status_code,
            status.HTTP_201_CREATED
        )
