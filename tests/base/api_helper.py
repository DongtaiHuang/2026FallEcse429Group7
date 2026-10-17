
import requests


class APIHelper:
    def __init__(self, base_url="http://localhost:4567"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get(self, endpoint, **kwargs):
        return self.session.get(
            f"{self.base_url}{endpoint}",
            timeout=5,
            **kwargs
        )

    def post(self, endpoint, data=None, **kwargs):
        return self.session.post(
            f"{self.base_url}{endpoint}",
            json=data,
            timeout=5,
            **kwargs
        )

    def put(self, endpoint, data=None, **kwargs):
        return self.session.put(
            f"{self.base_url}{endpoint}",
            json=data,
            timeout=5,
            **kwargs
        )

    def delete(self, endpoint, **kwargs):
        return self.session.delete(
            f"{self.base_url}{endpoint}",
            timeout=5,
            **kwargs
        )

    def close(self):
        self.session.close()
