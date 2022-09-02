import io
import unittest
from . import http_payload


class TestHttpPayload(unittest.TestCase):
	@staticmethod
	def chunk_to_parser(raw_request, parser):
		buf = io.StringIO(raw_request)
		while True:
			chunk = buf.read(5)
			if not chunk:
				break
			parser.feed(chunk)
		buf.close()

	def test_request_with_headers(self):
		raw_request = (
			"GET /resource HTTP/1.1\r\n"
			"Host: example.com\r\n"
			"Content-Type: text/plain\r\n"
			"\r\n"
		)

		payload = http_payload.HttpPayload()
		self.chunk_to_parser(raw_request, payload)

		self.assertTrue(len(payload.raw_headers) == 3)
		self.assertTrue(payload.headers['host'] == 'example.com')
		self.assertTrue(payload.headers['content-type'] == 'text/plain')
		self.assertTrue(payload.body_complete)

	def test_request_with_headers_and_body(self):
		raw_request = (
			"POST /resource HTTP/1.1\r\n"
			"Host: example.com\r\n"
			"Content-Type: text/plain\r\n"
			"Content-Length: 5\r\n"
			"\r\n"
			"abcde"
		)

		payload = http_payload.HttpPayload()
		self.chunk_to_parser(raw_request, payload)

		self.assertTrue(len(payload.raw_headers) == 4)
		self.assertTrue(payload.headers['host'] == 'example.com')
		self.assertTrue(payload.headers['content-type'] == 'text/plain')
		self.assertTrue(payload.headers['content-length'] == '5')
		self.assertTrue(payload.content_length == 5)
		self.assertTrue(payload.body == 'abcde')
		self.assertTrue(payload.body_complete)
