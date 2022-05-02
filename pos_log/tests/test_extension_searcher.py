from rest_framework.test import APITestCase
from datetime import datetime

from pos_log.modules.extension_searcher import \
    ExtensionLogSearcher

class TestClientsUnittest(APITestCase):

    """
        Writer: 하정현

        확장 집계 함수 테스트용
        TestCase
    """
    

    def test_aaa(self):
        """
            아무 의미 없는 함수 작동 확인용
            테스트

            테스트 케이스 추가하기 시작하면 삭제 예정
        """
        ExtensionLogSearcher.search_by_payment(
            time_range=(datetime.now(), datetime.now()),
            time_size='HOUR',
            price_range=(100,200),
            party_size=(200,300),
            restaurant_group='RES'
        )
        ExtensionLogSearcher.search_by_party(
            time_range=(datetime.now(), datetime.now()),
            time_size='HOUR',
            price_range=(100,200),
            party_size=(200,300),
            restaurant_group='RES'
        )