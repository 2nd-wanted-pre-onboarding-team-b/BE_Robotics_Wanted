from pos_log.tests.t_modules.extension_searcher import *
from pos_log.tests.tools.customed_api_testcase import CustomedAPITestCase
from pos_log.tests.tools.runner import test_runner
from typing import Dict

class TestExtensionSearcher(CustomedAPITestCase):
    """
        Writer: 하정현

        인원/결제수단 집계함수 테스트 코드
    """
    input_root: str = "pos_log/tests/inputs/query_expanded"
    input_files: Dict[str, str] = {
        "test_payment_validate": "query_search_payment_failed_params.json",
        "test_payment_result": "query_search_payment_result.json",
        "test_partysize_validate": "query_search_partysize_failed_params.json"
    }
    @classmethod
    def setUpTestData(cls):
        load_data(TestExtensionSearcher.input_root)

    @test_runner(test_func=check_payment_validate)
    def test_payment_validate(self):
        pass

    @test_runner(test_func=check_payment_result)
    def test_payment_result(self):
        pass

    @test_runner(test_func=check_partysize_validate)
    def test_partysize_validate(self):
        pass