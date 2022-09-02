import json
import unittest
from . import http_client
from . import http_payload


class TestHttpClient(unittest.IsolatedAsyncioTestCase):
	def test_make_stub_key(self):
		stub_key = http_client.Client.make_stub_key('get', 'www.example.com', '/')
		self.assertTrue(stub_key == 'GETwww.example.com/')

		stub_key = http_client.Client.make_stub_key('get', 'www.example.com', '/path?key=value')
		self.assertTrue(stub_key == 'GETwww.example.com/path?key=value')

	def test_add_stub(self):
		payload = http_payload.HttpPayload()
		payload.body = "test_ok"
		payload.status_code = 200

		client = http_client.Client()
		client.add_stub("GET", "www.example.com", "/resource", payload)

		payload = client.stubs['GETwww.example.com/resource'][0]
		self.assertTrue(payload.status_code == 200)
		self.assertTrue(payload.body == 'test_ok')

	def test_clear_stubs(self):
		client = http_client.Client()
		client.add_stub("GET", "example.com", "/", None)
		client.clear_stubs()
		self.assertTrue(len(client.stubs.keys()) == 0)

	async def test_request_with_stub(self):
		payload = http_payload.HttpPayload()
		payload.body = "test_ok"
		payload.status_code = 200

		client = http_client.Client()
		client.add_stub("GET", "example.com", "/", payload)

		payload = await client.request("GET", "example.com", "/")
		self.assertTrue(payload.status_code == 200)
		self.assertTrue(payload.body == "test_ok")

	async def test_live_request(self):
		client = http_client.Client()
		payload = await client.request("GET", "www.example.com", "/")
		self.assertTrue(payload.status_code == 200)

	async def test_list_post_request(self):
		client = http_client.Client()
		body = json.dumps({"test": "one"})
		payload = await client.request("POST", "postman-echo.com", "/post", body=body, with_json=True)
		self.assertTrue(payload.status_code == 200)
		d = json.loads(payload.body)
		self.assertTrue(d['json']['test'] == 'one')
