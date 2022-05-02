from datetime import datetime
from typing import Optional, Tuple, Set, Dict, Callable


class ExtensionLogSearcherValidator:
    """
        Writer: 하정현
        분석 요구사항에 적혀 있는 파라미터 유효성 검사 단일 함수

        Validate에 성공 시 True, 실패 시 False 제출
        Model에서 컬럼 데이터에 대한 type 검사하는 validator와는 다른 개념으로
        함수 입장에서 들어오는 input data에 대한 검증을 한다.
    """
    TIME_FORMAT: str = "%Y-%M-%d %h-%m-%s %f"
    TIME_SIZE: Set[str] = {'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'}

    @staticmethod
    def str2datetime(s: str) -> datetime:
        # string -> datetime
        if not s:
            return None
        return datetime.strptime(s, ExtensionLogSearcherValidator.TIME_FORMAT)

    @staticmethod
    def time_range_validator(time_range: Tuple[datetime, datetime]) -> bool:
        return True

    @staticmethod
    def time_size_validator(time_size: str) -> bool:
        return True

    @staticmethod
    def price_range_validator(price_range: Tuple[int, int]) -> bool:
        return True

    @staticmethod
    def party_size_validator(party_size: Tuple[int, int]) -> bool:
        return True

    @staticmethod
    def restaurant_group_validator(res_group: str) -> bool:
        return True

""" DECORATOR FUNCTIONS FOR USING """


"""
    Validator 함수 맵
    EX) 결제수단 집계를 진행할 때 time_range의 validator를 호출하려면
        VALIDATOR_MAPS['sb_payment']['time_range'](time_range)를 호출하면 된다.
"""
VALIDATOR_MAPS: Dict[str, Dict[str, Callable]] = {
    "sb_payment": {
        "time_range"    : ExtensionLogSearcherValidator.time_range_validator,
        "time_size"     : ExtensionLogSearcherValidator.time_size_validator,
        "price_range"   : ExtensionLogSearcherValidator.price_range_validator,
        "party_size"    : ExtensionLogSearcherValidator.party_size_validator,
        "restaurant_group"  : ExtensionLogSearcherValidator.restaurant_group_validator
    },
    "sb_partysize": {
        "time_range"    : ExtensionLogSearcherValidator.time_range_validator,
        "time_size"     : ExtensionLogSearcherValidator.time_size_validator,
        "price_range"   : ExtensionLogSearcherValidator.price_range_validator,
        "party_size"    : ExtensionLogSearcherValidator.party_size_validator,
        "restaurant_group"  : ExtensionLogSearcherValidator.restaurant_group_validator
    },
}

def sb_payment_validator(func):
    """
        결제수단 집계 함수 작동 시
        parameter 유효성 판별 함수

        필요한 param 없을 경우 TypeError
        validator에 Failed 했을 경우 ValueError
    """
    MUST_NEED_PARAMS = {"time_range", "time_size"}
    def wrapper(**kwargs):

        # parameter 존재 여부 검토
        for x in MUST_NEED_PARAMS:
            if x not in kwargs:
                raise TypeError(f"{x} not exists")

        # 각 parameter에 대한 검증
        for param in kwargs.keys():
            if not VALIDATOR_MAPS['sb_payment'][param](kwargs[param]):
                raise ValueError(f"Error by validate args: {param}: {kwargs[param]}")

        # run function
        res: Dict[str, object] = func(**kwargs)

        # TODO: 결과값 검토
        
        # 통과 되면 결과값 리턴
        return res

    return wrapper

def sb_partysize_validator(func):
    """
        인원 집계 함수 작동 시
        parameter 유효성 판별 함수

        필요한 param 없을 경우 TypeError
        validator에 Failed 했을 경우 ValueError
    """
    MUST_NEED_PARAMS = {"time_range", "time_size"}
    def wrapper(**kwargs):

        # parameter 존재 여부 검토
        for x in MUST_NEED_PARAMS:
            if x not in kwargs:
                raise TypeError(f"{x} not exists")

        # 각 parameter에 대한 검증
        for param in kwargs.keys():
            if not VALIDATOR_MAPS['sb_partysize'][param](kwargs[param]):
                raise ValueError(f"Error by validate args: {param}: {kwargs[param]}")

        # run function
        res: Dict[str, object] = func(**kwargs)

        # TODO: 결과값 검토
        
        # 통과 되면 결과값 리턴
        return res

    return wrapper

