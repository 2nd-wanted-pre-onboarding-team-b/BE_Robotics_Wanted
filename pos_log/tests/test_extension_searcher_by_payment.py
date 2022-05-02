from pos_log.tests.tools.converter import str2datetime
from pos_log.tests.tools.customed_api_testcase import CustomedAPITestCase
from pos_log.tests.tools.runner import test_runner
from pos_log.modules.extension_searcher import ExtensionLogSearcher
from typing import Dict

def check_validate(c: CustomedAPITestCase, time_range, time_size,
    price_range, party_size, restaurant_group):

    if time_range:
        # str을 datetime으로 변형
        for i in range(len(time_range)):
            time_range[i] = str2datetime(time_range[i])

    
    try:
        # 테스트 실행
        output = ExtensionLogSearcher.search_by_payment(
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
