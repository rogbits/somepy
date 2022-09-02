import lib.secret_store


def main():
	ss = lib.secret_store.SecretStore()
	ss.load()


if __name__ == "__main__":
	main()
