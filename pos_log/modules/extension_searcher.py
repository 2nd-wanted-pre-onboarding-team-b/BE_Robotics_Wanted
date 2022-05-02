from typing import Optional, Tuple, Dict, Set
from datetime import datetime
from pos_log.modules.extension_searcher_validator import *

class ExtensionLogSearcher:

    """
        Writer: 하정현
        Pos Log데이터를 이용한 확장 분석 메소드가 있는
        클래스
    """
    
    @staticmethod
    @sb_payment_validator
    def search_by_payment(
        time_range  : Tuple[datetime, datetime],
        time_size   : str,
        price_range : Optional[Tuple[int, int]] = None,
        party_size  : Optional[Tuple[int, int]] = None,
        restaurant_group    : Optional[str] = None
    ) -> Dict[str, object]:
        """
            결제수단 집계 함수

            param:
                time_range          : 시간 범위 (start, end)
                time_size           : HOUR, DAY, WEEK, MONTH, YEAR
                price_range         : 가격 범위 (min price, max price) [선택]
                party_size          : 결제 하나 당 인원 수 [선택]
                restaurant_group    : 식당 프랜차이즈 [선택]

            return:
                Dict 형태의 결과값
                Validate 실패 시 ValueError 호출
                필요한 param 없을 시 TypeError 호출
        """

        """
            input data에 대한 검증은 sb_payment_validator에서 진행했으므로
            바로 집계 작업에 들어간다.
        """

        # TODO: Call SQL Statement by ORM

        # TODO: make output data by result of SQL

        return {}

    @staticmethod
    @sb_partysize_validator
    def search_by_party(
        time_range  : Tuple[datetime, datetime],
        time_size   : str,
        price_range : Optional[Tuple[int, int]] = None,
        party_size  : Optional[Tuple[int, int]] = None,
        restaurant_group    : Optional[str] = None
    ) -> Dict[str, object]:
        """
            인원 집계 함수

            param:
                time_range          : 시간 범위 (start, end)
                time_size           : HOUR, DAY, WEEK, MONTH, YEAR
                price_range         : 가격 범위 (min price, max price) [선택]
                party_size          : 결제 하나 당 인원 수 [선택]
                restaurant_group    : 식당 프랜차이즈 [선택]

            return:
                Dict 형태의 결과값
                Validate 실패 시 ValueError 호출
                필요한 param 없을 시 TypeError 호출
        """

        
        """
            input data에 대한 검증은 sb_partysize_validator에서 진행했으므로
            바로 집계 작업에 들어간다.
        """

        # TODO: Call SQL Statement by ORM

        # TODO: make output data by result of SQL

        return {}