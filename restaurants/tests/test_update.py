from rest_framework.test import APITestCase
from rest_framework import status

from restaurants.models import *
from restaurants.serializers import RestaurantSerializer
group_id4test = -1
restaurant_id4test = -1

class TestRestaurantCreate(APITestCase):
    API = '/api/restaurants'
    GROUP_NAME = 'my-group'

    @classmethod
    def setUpTestData(cls):
        global group_id4test
        global restaurant_id4test

        # group 생성
        __group = Group.objects.create(group_name=TestRestaurantCreate.GROUP_NAME)
        group_id4test = __group.id
        
        req = {
            'group': group_id4test,
            'city': 'Seoul',
            'restaurant_name': '식당',
            'address': '서초구'
        }
        s = RestaurantSerializer(data=req)
        s.is_valid(raise_exception=True)
        s.save()

        # 테스트에 사용될 아이디 저장
        restaurant_id4test = s.data['id']

    def test_update_no_found(self):
        # 해당 식당을 찾을 수 없음
        req = {
            'city': 'Busan',
        }
        self.assertEqual(
            self.client.patch(f'{self.API}/99999999', data=req).status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_do_not_modify_create_date(self):
        # 생성 시간 수정되어선 안됨
        req = {'created': '1997-09-04 12:12:12'}
        res = self.client.patch(f'{self.API}/{restaurant_id4test}', data=req)
        self.assertEqual(res.status_code, 400, msg=res.json())

    def test_do_not_modify_modified_date(self):
        # 수정 시간 수정되어선 안됨
        req = {'modified': '1997-09-04 12:12:12'}
        res = self.client.patch(f'{self.API}/{restaurant_id4test}', data=req)
        self.assertEqual(res.status_code, 400, msg=res.json())

    def test_update_success(self):
        # 수정 성공
        req = {
            'city': 'Busan',
            'address':' 남구',
            'restaurant_name': '남구 식당',
        }
        res = self.client.patch(f'{self.API}/{restaurant_id4test}', data=req)
        self.assertEqual(res.status_code, 200, msg=res.json())