import io
import asyncio
from . import http_payload


class Server:
	def __init__(self):
		self.server = None
		self.user_handler = None
		pass

	def on_request(self, handler_fn):
		self.user_handler = handler_fn

	async def handler(self, reader, writer):
		payload = http_payload.HttpPayload()
		while True:
			chunk = await reader.read(io.DEFAULT_BUFFER_SIZE)
			payload.feed(chunk.decode('utf8'))
			if payload.body_complete:
				break

		await self.user_handler(payload, writer, self)

	def stop(self):
		self.server.close()

	async def start(self, port):
		server = await asyncio.start_server(self.handler, '0.0.0.0', '8080')
		addresses = ', '.join(str(sock.getsockname()) for sock in server.sockets)
		print(f'Serving on {addresses}')
		self.server = server
		try:
			await server.serve_forever()
		except asyncio.CancelledError:
			pass
