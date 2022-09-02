import asyncio
import lib.http_client


async def main():
	client = lib.http_client.Client()
	payload = await client.request("GET", "www.example.com")
	print(payload.status_code)


if __name__ == "__main__":
	asyncio.run(main())
