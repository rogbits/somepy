class HttpPayload:
	def __init__(self):
		# payload properties
		self.raw_headers = [""]
		self.headers = {}
		# request start-line
		self.method = ""
		self.path = ""
		self.proto = ""

		# response start-line
		self.proto = ""
		self.status_code = 0
		self.reason = ""

		self.body = ""
		self.content_length = 0

		# header state
		self.parsing_headers = True
		self.start_of_line = True
		self.carriage_return = False
		self.end_of_headers = False

		# body state
		self.body_complete = False

		self.in_debug = False

	def feed(self, chunk):
		self.debug('incoming', repr(chunk))
		for c in chunk:
			self.process_char(c)

	def process_char(self, c):
		self.debug("processing", repr(c))

		# carriage return
		if c == '\r':
			self.carriage_return = True
			if self.parsing_headers and self.start_of_line:
				self.debug("setting end of headers flag")
				self.end_of_headers = True
			if not self.parsing_headers:
				self.debug('adding to body', repr(c))
				self.body += c
				self.check_for_complete_body()
			return

		# new line
		if c == '\n':
			if self.parsing_headers and self.end_of_headers:
				self.debug("reached end of headers")
				self.raw_headers.pop()
				self.parsing_headers = False
				self.process_raw_headers()
				return
			if self.parsing_headers and self.carriage_return:
				self.debug("header complete")
				self.start_of_line = True
				self.carriage_return = False
				self.raw_headers.append("")
				return

			self.debug("adding to body", repr(c))
			self.body += c
			self.check_for_complete_body()
			return

		# other characters
		self.start_of_line = False
		if self.parsing_headers:
			self.debug("adding", repr(c), "to header number", len(self.raw_headers) - 1)
			self.raw_headers[-1] += c
			return
		else:
			self.debug("adding to body", c)
			self.body += c
			self.check_for_complete_body()
			return

	def process_raw_headers(self):
		start_line = self.raw_headers[0]
		split = start_line.split()
		if split[0].lower().startswith('http'):
			# response start-line
			self.proto, self.status_code, self.reason = split
			self.status_code = int(self.status_code)
		else:
			# request start-line
			self.method, self.path, self.proto = split

		self.method, self.path, self.proto = start_line.split()
		self.method = self.method.upper()

		for header in self.raw_headers[1:]:
			key, value = header.split(': ', 1)
			self.headers[key.lower()] = value

		if 'content-length' in self.headers:
			self.content_length = int(self.headers['content-length'])

		if self.content_length == 0:
			self.body_complete = True

	def check_for_complete_body(self):
		self.debug(
			"checking for complete body,",
			"content length:", self.content_length,
			"body length:", len(self.body),
			"equal:", self.content_length == len(self.body)
		)
		self.body_complete = self.content_length == len(self.body)

	def debug(self, *args):
		if self.in_debug:
			print(" ".join(map(str, args)))
