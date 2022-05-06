from rest_framework.test import APITestCase
from rest_framework import status

from .models import Menu
from pos_log.models import PosLog, PosLogMenu
from restaurants.models import Group, Restaurant


APITestCase.maxDiff = None

class MenuSalesTestCase(APITestCase):
    def setUp(self):
        self.group_bibigo = Group.objects.create(group_name="비비고")
        self.group_vibs_burger = Group.objects.create(group_name="빕스버거")

        self.menu_vibs_burger_01 = Menu.objects.create(menu_name="버거", price="10000", group=self.group_vibs_burger)
        self.menu_vibs_burger_02 = Menu.objects.create(menu_name="불고기버거", price="10000", group=self.group_vibs_burger)
        self.menu_bibigo_01 = Menu.objects.create(menu_name="제육덮밥", price="10000", group=self.group_bibigo)
        self.menu_bibigo_02 = Menu.objects.create(menu_name="갈비비빔밥", price="15000", group=self.group_bibigo)

        self.restaurant_bibigo_01 = Restaurant.objects.create(
            restaurant_name = "비비고_서초점",
            city = "서울",
            address = "서초구 서초동",
            group = self.group_bibigo
            )
        self.restaurant_bibigo_02 = Restaurant.objects.create(
            restaurant_name = "비비고_신림점", 
            city = "서울", 
            address = "관악구 신림동", 
            group = self.group_bibigo
            )
        self.restaurant_vibs_burger_01 = Restaurant.objects.create(
            restaurant_name = "빕스버거_개포점", 
            city = "서울", 
            address = "강남구 개포동", 
            group = self.group_vibs_burger
            )
        self.restaurant_vibs_burger_02 = Restaurant.objects.create(
            restaurant_name = "빕스버거_신림점", 
            city = "서울", 
            address = "관악구 신림동", 
            group = self.group_vibs_burger
            )

        pos_log_01 = PosLog.objects.create(            
            price = 25000,
            number_of_party = 2,
            payment = "CARD",
            restaurant_id = self.restaurant_bibigo_01.id)
        for i in [self.menu_bibigo_01, self.menu_bibigo_02]:
            poslogmenu = PosLogMenu(pos_log=pos_log_01, menu=i, count=1)
            poslogmenu.save()

        pos_log_02 = PosLog.objects.create(            
            price = 20000,
            number_of_party = 2,
            payment = "CARD",
            restaurant_id = self.restaurant_vibs_burger_02.id)
        poslogmenu = PosLogMenu(pos_log=pos_log_02, menu=self.menu_vibs_burger_01, count=2)
        poslogmenu.save()

        pos_log_03 = PosLog.objects.create(            
            price = 20000,
            number_of_party = 2,
            payment = "CARD",
            restaurant_id = self.restaurant_vibs_burger_01.id)
        poslogmenu = PosLogMenu(pos_log=pos_log_03, menu=self.menu_vibs_burger_02, count=2)
        poslogmenu.save()

        pos_log_04 = PosLog.objects.create(            
            price = 35000,
            number_of_party = 3,
            payment = "CARD",
            restaurant_id = self.restaurant_bibigo_02.id)
        poslogmenu = PosLogMenu(pos_log=pos_log_04, menu=self.menu_bibigo_01, count=2)
        poslogmenu.save()
        poslogmenu = PosLogMenu(pos_log=pos_log_04, menu=self.menu_bibigo_02, count=1)
        poslogmenu.save()

        pos_log_05 = PosLog.objects.create(            
            price = 25000,
            number_of_party = 2,
            payment = "CARD",
            restaurant_id = self.restaurant_bibigo_01.id)
        poslogmenu = PosLogMenu(pos_log=pos_log_05, menu=self.menu_bibigo_01, count=1)
        poslogmenu.save()
        poslogmenu = PosLogMenu(pos_log=pos_log_05, menu=self.menu_bibigo_02, count=1)
        poslogmenu.save()

        pos_log_06 = PosLog.objects.create(            
            price = 20000,
            number_of_party = 2,
            payment = "CARD",
            restaurant_id = self.restaurant_vibs_burger_01.id)
        poslogmenu = PosLogMenu(pos_log=pos_log_06, menu=self.menu_vibs_burger_02, count=2)
        poslogmenu.save()

        for pos_log in [pos_log_01, pos_log_02]:
            pos_log.timestamp = "2022-02-01"
            pos_log.save()
        
        for pos_log in [pos_log_03, pos_log_04]:
            pos_log.timestamp = "2022-02-02"
            pos_log.save()

        for pos_log in [pos_log_05, pos_log_06]:
            pos_log.timestamp = "2022-02-03"
            pos_log.save()

    def test_menu_sales(self):
        response = self.client.get("/api/menu/sales?menu-list=1,2,3,4&start-time=2022-02-01&end-time=2022-02-02&order=-total_price")
        self.assertCountEqual(response.json(), [
            {'poslogmenu__menu': 3, 'total_price': 30000, 'menu_name': '제육덮밥'}, 
            {'poslogmenu__menu': 4, 'total_price': 30000, 'menu_name': '갈비비빔밥'}, 
            {'poslogmenu__menu': 1, 'total_price': 20000, 'menu_name': '버거'}, 
            {'poslogmenu__menu': 2, 'total_price': 20000, 'menu_name': '불고기버거'}
            ]
        )

        response = self.client.get("/api/menu/sales?menu-list=1,2,3,4&start-time=2022-02-02&end-time=2022-02-03&order=-total_price")
        self.assertCountEqual(response.json(), [
            {'poslogmenu__menu': 2, 'total_price': 40000, 'menu_name': '불고기버거'},
            {'poslogmenu__menu': 3, 'total_price': 30000, 'menu_name': '제육덮밥'}, 
            {'poslogmenu__menu': 4, 'total_price': 30000, 'menu_name': '갈비비빔밥'}
            ]
        )

        response = self.client.get("/api/menu/sales?menu-list=3,4&start-time=2022-02-01&end-time=2022-02-03&order=-total_price")
        self.assertCountEqual(response.json(), [
            {'poslogmenu__menu': 4, 'total_price': 45000, 'menu_name': '갈비비빔밥'},
            {'poslogmenu__menu': 3, 'total_price': 40000, 'menu_name': '제육덮밥'}
            ]
        )

        response = self.client.get("/api/menu/sales?menu-list=3,4&start-time=2022-02-03&end-time=2022-02-01&order=-total_price")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get("/api/menu/sales?menu-list=&start-time=2022-02-03&end-time=2022-02-01&order=-total_price")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get("/api/menu/sales?start-time=2022-02-03&end-time=2022-02-01&order=-total_price")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)