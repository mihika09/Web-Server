import Server


def display_get(request, response):
	return 'Hello, World'


def display_post(request, response):
	return request['body']


def add_nos(request, response):

	try:
		s = 0
		try:
			for i in request['body']:
				s = s + int(request['body'][i])
		except ValueError:
			for i in request['body']:
				s = s + float(request['body'][i])

	except ValueError:
		s = ''
		for i in request['body']:
			s = s + (request['body'][i]) + ' '

	print("s: ", s)
	return s


Server.add_route("GET", "/some", display_get)
Server.add_route("POST", "/some", display_post)
Server.add_route("POST", "/add", add_nos)

# Server.add_route("PUT", "/some", display_post)
Server.start_server()