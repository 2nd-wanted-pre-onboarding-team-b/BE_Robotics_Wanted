from rest_framework.test import APITestCase
from abc import ABC
from typing import Dict

class CustomedAPITestCase(APITestCase, ABC):
    input_root: str
    input_files: Dict[str, str]