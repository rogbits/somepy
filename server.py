import asyncio
import lib.http_client
import lib.http_server
import lib.http_payload


async def handler(payload: lib.http_payload.HttpPayload, writer, server: lib.http_server.Server):
	print(payload.raw_headers)
	writer.write(b"HTTP/1.1 200 OK\n")
	writer.write(b"Content-Length: 5\n")
	writer.write(b"Connection: close\n")
	writer.write(b"Content-Type: text/html\n")
	writer.write(b"\n")
	writer.write(b"hello")
	await writer.drain()
	writer.close()
	server.stop()


async def main():
	server = lib.http_server.Server()
	server.on_request(handler)
	await server.start(8080)


if __name__ == "__main__":
	asyncio.run(main())
