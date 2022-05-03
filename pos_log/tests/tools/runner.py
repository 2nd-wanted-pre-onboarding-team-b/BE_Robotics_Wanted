from pos_log.tests.tools.customed_api_testcase import CustomedAPITestCase
from typing import Callable, Iterable, Dict, List, Sequence
from collections import deque
import json

"""
    Writer: 하정현
    Summary: Test Runner Decorator Function
"""

def __validator_certain_type(t, a) -> Callable:
    """
        answer의 Type에 따른 assert함수 리턴
    """
    if isinstance(a, Dict):
        return t.assertDictContainsSubset
    elif isinstance(a, Sequence):
        return t.assertSequenceEqual
    else:
        return t.assertEqual

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
                topic, ipt, answer = case['topic'], case['input'], case['answer']
                # 테스트 함수 실행
                output = test_func(test_e, **ipt)
                # 에러 메세지
                err_msg: str \
                    = f"\n\nIn Topic: {topic}\ninput: {ipt}\noutput: {output}\nbut answer: {answer}"
                # output 데이터가 일치한 지 검토
                __validator_certain_type(test_e, answer)(answer, output, msg=err_msg)
            return func(test_e)
        return __wrapper
    return __test_runner