from rest_framework import status
from rest_framework.test import APIClient


class PublicAPIAccessTest:

    @property
    def endpoint(self):
        raise NotImplementedError()

    def setUp(self):
        self.client = APIClient()

    expected_status_code = status.HTTP_200_OK
    payload = {}

    def test_list_api_access(self):
        res = self.client.get(self.endpoint)
        self.assertEquals(res.status_code, self.expected_status_code)

    def test_model_create_access(self):
        res = self.client.post(self.endpoint, self.payload)
        self.assertEquals(res.status_code, self.expected_status_code)
