import uuid
import json


class SecretStore:
	path = 'secrets.json'

	def __init__(self):
		self.storage = {
			"test": "one"
		}

	def save(self):
		with open(SecretStore.path, "w+") as file:
			file.write(json.dumps(self.storage))

	def load(self):
		with open(SecretStore.path, "r+") as file:
			data = file.read()
			self.storage = json.loads(data)

	def get_secret_id(self):
		return uuid.uuid4()

	def store_secret(self, user: str, secret_value: str) -> str:
		"""Stores a secret in a SecretStore and returns the secret id"""
		secret_id = str(self.get_secret_id())
		if user not in self.storage:
			self.storage[user] = {}

		self.storage[user][secret_id] = secret_value
		return secret_id

	def get_secret(self, user: str, secret_id: str) -> str:
		"""Returns the secret value, if the user can access the secret."""
		return self.storage[user][secret_id]
