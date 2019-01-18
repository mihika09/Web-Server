import socket


def start_line_parser(s):

	try:
		method = s[0]
		request_target = s[1]
		http_version = s[2]
		print("method: ", method, "request_target: ", request_target, "http_version: ", http_version)
		return (method, request_target, http_version)

	except err:
		print("err: ", err)
		return -1


def header_parser(request):

	request = request
	dct = {}
	for i in request:
		x = i.index(':')
		key = i[0:x].strip()
		value = i[x+1:].strip()
		dct[key] = value

	print("dct: ",dct)


def request_parser(request):
	x = request.index('\n')
	s = request[0:x].strip().split()
	slp = start_line_parser(s)
	if slp == -1:
		print("Bad Request")
		return -1

	else:
		request = request[x+1:].strip().split('\n')
		header_parser(request)
		return slp[1]

		

PORT = 8888
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', PORT))
sock.listen(1)
print("Serving on HTTP port: ", PORT)
while True:
	cliconn, cliaddr = sock.accept()
	request = cliconn.recv(1024).decode()
	# print("Request: ", request)
	res = request_parser(request)

	if res == -1:
		sys.exit()

	if res == '/':
		res = '/index.html'

	try:
		fin = open(res[1:])
		content = fin.read()
		fin.close()

	except FileNotFoundError:
		content = '<h1>File Not Found</h1>'

	http_response = 'HTTP/1.1 200 OK\n\n' + content
	
	cliconn.send(http_response.encode())
	cliconn.close()
