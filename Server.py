import socket

HOST = ''
PORT = 8888


def get_handler(dct, req):

	if len(req) > 0:
		return "Message Body not expected"

	if dct["Request_Target"] == '/':
		dct["Request_Target"] += "index.html"

	filepath = '/Users/mallikamohta/Desktop/Mihika/Static'+dct["Request_Target"]
	print("filepath: ", filepath)
	try:
		file = open(filepath)
		content = file.read()
		file.close()

	except FileNotFoundError:
		content = "Page not found"

	return content


def request_header_handler(req, dct):

	y = req.index('\r\n\r\n')

	header = req[0:y]
	header = header.split('\r\n')
	print("\nHeader now: ", header)

	req = req[y:]

	if req[0:4] == '\r\n\r\n':
		req = req[4:]
		print("Request: ", req)
		body_len = len(req)
		print("Body_Len: ", body_len)

	else:
		print("Bad request")
		return None

	try:
		for i in header:
			# print("i: ", i)
			if i:
				key = i[0: i.index(':')]
				value = i[i.index(':')+1:]
				dct[key] = value

	except:
		print("Bad Request")
		return None

	if "Content-Length" not in dct:
		conlen = 0

	else:
		conlen = dct["Content-Length"]

	if conlen != body_len:
		print("Bad request: expected no message body")
		return None

	return dct, req


def request_handler(req):

	dct = {}
	x = req.index('\n')

	try:
		sl = req[0:x].split()
		if len(sl) == 3:
			dct["Method"] = sl[0]
			dct["Request_Target"] = sl[1]
			dct["Http_Version"] = sl[2]
		else:
			raise Exception

	except:
		print("Bad Request")

	req = req[x+1:]
	res = request_header_handler(req, dct)
	if res is not None:
		dct = res[0]
		req = res[1]

	if dct["Method"] == 'GET':
		get_res = get_handler(dct, req)
		return get_res


if __name__ == '__main__':

	listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listen_socket.bind((HOST, PORT))
	listen_socket.listen(5)
	print("Listening on port: ", PORT)

	try:
		while True:
			cliconn, cliaddr = listen_socket.accept()
			request = cliconn.recv(1024).decode()
			response = request_handler(request)
			if response is not None:
				http_response = "HTTP/1.1 200 OK\r\n"+'Content-Type: text/html\r\n\r\n'+response+'\r\n'
				cliconn.send(http_response.encode())
			else:
				http_response = "HTTP/1.1 200 OK\r\n" + "Bad Request"
			cliconn.close()

	except KeyboardInterrupt:
		print("Shutting down server")
