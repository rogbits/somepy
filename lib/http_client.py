import io
import asyncio
from . import http_payload


class Client:
	def __init__(self):
		self.stubs = {}

	@staticmethod
	def make_stub_key(method, host, path):
		return method.upper() + host + path

	def add_stub(self, method, host, path, payload):
		key = self.make_stub_key(method, host, path)
		if key not in self.stubs:
			self.stubs[key] = []
		self.stubs[key].append(payload)

	def clear_stubs(self):
		self.stubs = {}

	@staticmethod
	def parse_response(resp):
		raw_headers = []
		headers = {}
		body = ""
		buf = io.StringIO(resp)
		parsing_headers = True
		while True:
			line = buf.readline()
			if not line:
				break
			if line == "\r\n":
				parsing_headers = False
				continue
			if parsing_headers:
				header = line.rstrip("\r\n")
				raw_headers.append(header)
				split = header.split(':', 1)
				if len(split) > 1:
					headers[split[0]] = split[1]
			else:
				body += line

		status_code = raw_headers[0].split()[1]
		reason = raw_headers[0].split()[2]
		return int(status_code), reason, headers, body

	async def request(
			self, method, host, path="/", headers=None, body=None,
			port=443, ssl=True, with_json=False
	) -> http_payload.HttpPayload:

		stub_key = self.make_stub_key(method, host, path)
		if stub_key in self.stubs and len(self.stubs[stub_key]) > 0:
			return self.stubs[stub_key].pop(0)

		# open async connection
		reader, writer = await asyncio.open_connection(host, port, ssl=ssl)

		# raw request
		raw_request = (
			f"{method.upper()} {path} HTTP/1.1\r\n"
			f"Host: {host}\r\n"
			f"User-Agent: python\r\n"
			f"Connection: close\r\n"
		)
		if with_json:
			raw_request += f"Content-Type: application/json\r\n"
		if body:
			raw_request += f"Content-Length: {len(body)}\r\n"
		if headers is None:
			headers = {}
		for key, value in headers.items():
			raw_request += f"{key}: {value}\r\n"
		raw_request += f"\r\n"

		if body:
			raw_request += body

		# write request to host
		start, end = 0, io.DEFAULT_BUFFER_SIZE
		while True:
			chunk = raw_request[start:end]
			if not chunk:
				break
			writer.write(chunk.encode('utf8'))
			await writer.drain()
			start = end
			end = start + io.DEFAULT_BUFFER_SIZE

		payload = http_payload.HttpPayload()
		while True:
			chunk = await reader.read(io.DEFAULT_BUFFER_SIZE)
			payload.feed(chunk.decode('utf8'))
			if payload.body_complete:
				break

		writer.close()
		return payload
