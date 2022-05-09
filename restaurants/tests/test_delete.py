from rest_framework.test import APITestCase
from rest_framework import status
from restaurants.models import Group
from restaurants.serializers import RestaurantSerializer

group_id4test = -1

class TestRestaurantCreate(APITestCase):
    API = '/api/restaurants'
    GROUP_NAME = 'my-group'

    @classmethod
    def setUpTestData(cls):
        global group_id4test
        __group = Group.objects.create(group_name=TestRestaurantCreate.GROUP_NAME)
        group_id4test = __group.id

    
    def test_not_found(self):
        self.assertEqual(
            self.client.delete(f'{self.API}/99999').status_code,
            status.HTTP_404_NOT_FOUND
        )
    
    def test_delete(self):
        req = {
            'group': group_id4test,
            'city': 'Seoul',
            'restaurant_name': '식당',
            'address': '서초구'
        }
        s = RestaurantSerializer(data=req)
        s.is_valid(raise_exception=True)
        s.save()
        target_id = s.data['id']

        self.assertEqual(self.client.delete(f'{self.API}/{target_id}').status_code, 204)