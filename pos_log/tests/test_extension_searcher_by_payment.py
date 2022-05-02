from pos_log.tests.tools.customed_api_testcase import CustomedAPITestCase
from pos_log.tests.tools.runner import test_runner

from typing import Dict

def check_validate(c: CustomedAPITestCase, time_range, time_size,
    price_range, party_size, restaurant_group):
    print(c)

class TestExtensionSearcherByPayment(CustomedAPITestCase):

    """
        Writer: 하정현

        인원 집계함수 테스트 코드
    """
    def __init__(self, *args, **kwargs):
        super(TestExtensionSearcherByPayment, self).__init__(*args, **kwargs)

        self.input_root: str = "pos_log/tests/inputs/query"
        self.input_files: Dict[str, str] = {
            "test_validate": "query_search_payment_failed_params.json"
        }

    @test_runner(test_func=check_validate)
    def test_validate(self):
        pass
