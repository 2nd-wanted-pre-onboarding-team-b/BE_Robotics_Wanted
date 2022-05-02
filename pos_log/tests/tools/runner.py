from pos_log.tests.tools.customed_api_testcase import CustomedAPITestCase
from typing import Callable, Iterable, Dict
from collections import deque

import json

def test_runner(test_func : Callable):

    def __test_runner(func: Callable):
        def __wrapper(test_e: CustomedAPITestCase):
            
            # 테스트 파일
            test_f: str = f"{test_e.input_root}/{test_e.input_files[func.__name__]}"

            # 테스트 케이스 가져오기
            with open(test_f, 'rt') as f:
                cases = json.load(f)['case']

            for case in cases:
                # 테스트 케이스 마다 실행
                test_func(test_e, **case["input"])

            return func(test_e)
        return __wrapper
    return __test_runner