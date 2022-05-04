from rest_framework.test import APITestCase
from rest_framework import status
from menu.models import *
from pos_log.models import *
from restaurants.models import *
from django.db import connection

import csv
import json

"""
Writer: 하정현

인원/결제수단 집계함수 테스트 코드
"""
def load_data(i_root):
    """
    테스트 돌리기 전, DB에 테스트용 데이터 업로드
    """
    # Group 생성
    with open(f"{i_root}/test_group.csv", "rt") as f:
        reader = csv.reader(f)
        for g_name in reader:
            if g_name == 'group_name':
                continue
            g = Group(group_name = g_name)
            g.save()

    # 식당 생성
    with open(f"{i_root}/test_res.csv", "rt") as f:
        reader = csv.reader(f)
            
        for gi, n, c, a in reader:
            if gi == 'group_id':
                continue
            r = Restaurant(
                group=Group.objects.get(id=int(gi)),
                restaurant_name=n,
                city=c,
                address=a
            )
            r.save()

    # Log 생성
    with open(f"{i_root}/test_log.csv", 'rt') as f:
        reader = csv.reader(f)
        i = 1
        for t, ri, p, nop, pay in reader:
            if t == 'timestamp':
                continue
                
            # id 자동생성 문제로 인하여 Raw Query로 해결
            with connection.cursor() as cursor:
                s = f"INSERT INTO pos_log VALUES ({i},'{t}',{p},{nop},'{pay}',{ri})"
                cursor.execute(s)
            i += 1

class TestExtensionSearcher(APITestCase):

    INPUT_ROOT  = "pos_log/tests/inputs/expanded_searcher"
    API         = "/api/pos"
    ERR_MSG     = "Topic: {0}\nInput: {1}\nAnswer: {2}\nOutput: {3}\n"

    @classmethod
    def setUpTestData(cls):
        # 테스트 전 DB에 테스트 할 데이터 업로드
        load_data(TestExtensionSearcher.INPUT_ROOT)

    def tcase_runner(self, api, test_file):
        """
        테스트 케이스 정보 제너레이터
        테스트 케이스를 실행한 결과물들을 출력
        """

        # 테스트 케이스가 들어있는 JSON 파일
        test_case_root = f"{self.INPUT_ROOT}/{test_file}"

        # json LOAD
        with open(test_case_root, "rt") as f:
            test_cases = json.load(f)['case']
            for case in test_cases:
                """
                topic: 테스트 주제
                input: input data
                output: 출력
                answer: 정답
                """
                topic, input_data, answer = \
                    case['topic'], case['input'], case['answer']
                url = f"{self.API}/{api}"
                output = self.client.get(url, input_data)
                yield topic, input_data, output, answer

    def test_wrong_url(self):
        """
        잘못된 search url
        """
        self.assertEqual(self.client.get(f"{self.API}/aaaaaa").status_code, 
            status.HTTP_400_BAD_REQUEST)

    def test_payment_numberofparty_validate(self):
        """
        payment 분석 API에 대한 validate 검사 테스트
        유효성 판별 테스트로 status code만 검토

        party, payment둘 다 동일한 예외처리를 가지므로
        하나만 돌린다.
        """
        for topic, input_data, output, answer \
            in self.tcase_runner("payment", "payment_partysize_validate.json"):
                self.assertEqual(
                    output.status_code, answer, 
                    msg=self.ERR_MSG.format(topic, input_data, answer, output.status_code))

    def test_payment_result(self):
        """
        payment 쿼리 결과에 대한 테스트
        status code, 결과 까지 전부 검토
        """
        for topic, input_data, output, answer \
            in self.tcase_runner("payment", "payment_result.json"):

                # 항상 200이 나와야 한다
                self.assertEqual(
                    output.status_code, status.HTTP_200_OK, 
                    msg=self.ERR_MSG.format(
                        topic, input_data, status.HTTP_200_OK, output.status_code))

                # 데이터가 올바르게 출력되는 지 검토
                self.assertCountEqual(
                    output.json(), answer,
                    msg=self.ERR_MSG.format(topic, input_data, answer, output.json()))

    def test_number_of_party_result(self):
        """
        party 쿼리 결과에 대한 테스트
        status code, 결과 까지 전부 검토
        """
        for topic, input_data, output, answer \
            in self.tcase_runner("number-of-party", "partysize_result.json"):

                # 항상 200이 나와야 한다
                self.assertEqual(
                    output.status_code, status.HTTP_200_OK, 
                    msg=self.ERR_MSG.format(
                        topic, input_data, status.HTTP_200_OK, output.status_code))

                # 데이터가 올바르게 출력되는 지 검토
                self.assertCountEqual(
                    output.json(), answer,
                    msg=self.ERR_MSG.format(topic, input_data, answer, output.json()))

