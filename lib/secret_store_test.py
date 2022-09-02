import uuid
import unittest
from unittest.mock import MagicMock
from . import secret_store


class TestSecretStore(unittest.TestCase):
	def test_save(self):
		ss = secret_store.SecretStore()
		ss.storage = {
			"user1": {
				"secret_id1": "secret1",
				"secret_id2": "secret2"
			}
		}

		ss.save()
		with open(secret_store.SecretStore.path, "r+") as file:
			data = file.read()
			expected = '{"user1": {"secret_id1": "secret1", "secret_id2": "secret2"}}'
			self.assertTrue(data == expected)

	def test_load(self):
		ss = secret_store.SecretStore()
		ss.load()
		self.assertTrue(ss.storage['user1']['secret_id1'] == "secret1")
		self.assertTrue(ss.storage['user1']['secret_id2'] == "secret2")

	def test_get_next_id(self):
		saved = uuid.uuid4
		ss = secret_store.SecretStore()
		uuid.uuid4 = MagicMock(return_value="aaaa-aaaa")
		secret_id = ss.get_secret_id()
		self.assertTrue(secret_id == 'aaaa-aaaa')
		uuid.uuid4 = saved

	def test_store_secret(self):
		ss = secret_store.SecretStore()
		user = 'john'
		secret_id = ss.store_secret('john', 'password')
		self.assertTrue(ss.storage[user][secret_id] == 'password')

	def test_get_secret(self):
		ss = secret_store.SecretStore()
		user = 'john'
		secret_id = ss.store_secret('john', 'password')
		secret = ss.get_secret(user, secret_id)
		self.assertTrue(secret == 'password')
