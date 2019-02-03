from email.utils import formatdate
import json
import asyncio
import pprint
import mimetypes
host = '127.0.0.1'
port = 8888


METHODS = ['GET', 'POST']
ROUTES = {method: {} for method in METHODS}


def add_route(method, route, controller):
	# print("method: ", method, "route: ", route, "controller: ", controller)
	ROUTES[method][route] = controller


def route_handler(request, response):

	method = request['method']
	controller = request["request_target"]
	print("controller: ", controller)
	print("method: ", method)
	print("ROUTES[method]: ", ROUTES[method])

	if controller in ROUTES[method]:
		response['body'] = ROUTES[method][controller](request, response)
		response['body'] = str(response['body']).encode()
		response = response_200_ok(response) + response['body']
		return response

	return None


def generate_encoded_response(response):

	enc_res = response['http_version']+" "+response['status']+'\r\n'
	for i, j in response['header'].items():
		enc_res = enc_res + i + ": " + str(j) + "\r\n"

	enc_res = enc_res+'\r\n'
	enc_res = enc_res.encode()
	return enc_res


def add_response_headers(response):

	response['http_version'] = 'HTTP/1.1'
	response['header']['Date'] = formatdate(usegmt=True)
	response['header']['Connection'] = 'close'
	response = generate_encoded_response(response)
	return response


def response_404_not_found(response):

	response['status'] = '404 Not Found'
	response['header']['Content-Length'] = str(0)
	response = add_response_headers(response)
	return response


def response_200_ok(response):

	response['status'] = '200 OK'
	if response['body']:
		response['header']['Content-Length'] = str(len(response['body']))

	response = add_response_headers(response)
	return response


def static_file_handler(request, response):

	if request['method'] == 'GET':

		file_path = '/Users/mallikamohta/Desktop/Mihika/Static' + request["request_target"]
		try:
			with open(file_path, 'rb') as file:
				content = file.read()

			response['body'] = content
			response['header']['Content-Type'] = mimetypes.guess_type(request['request_target'])[0]
			response = response_200_ok(response) + response['body']
			return response

		except FileNotFoundError:
			return None

	return None


def generate_response(request):

	response = {'header': {}}

	returned_response = static_file_handler(request, response)
	if returned_response is None:
		returned_response = route_handler(request, response)
		if returned_response is None:
			returned_response = response_404_not_found(response)

	response = returned_response
	return response


"""def form_parser(request):

	pprint.pprint(request)
	print("\n\n\n")
	boundary = (request['content-type'].split(';')[-1]).split('=')[-1]
	print("boundary: ", boundary)
	print("\n\n\n")
	form_list = request['body'].decode().split(boundary)[1:-1]
	print("form_list: ", form_list)
	print("\n\n\n")
	return request"""


def body_parser(request):

	if request['content-type'] == 'text/plain':
		request['body'] = str(request['body'])

	elif request['content-type'] == 'application/json':
		request['body'] = json.loads(request['body'])

	elif request['content-type'] == 'application/x-www-form-urlencoded':
		request['body'] = request['body'].decode()
		request['body'] = dict(query.split('=') for query in request['body'].split('&'))

	# elif request['content-type'][0:request['content-type'].index(';')] == 'multipart/form-data':
	# 	request['body'] = form_parser(request)

	return request['body']


def query_parser(request):

	path, query = request.split("?")
	q = dict(a.split("=") for a in query.split("&"))
	return path, q


def request_parser(header_stream):
	req_line, *req_header = header_stream.split('\r\n')
	request = dict(zip(['method', 'request_target', 'http_version'], req_line.split()))

	if '?' in request['request_target']:
		request['request_target'], request['query_content'] = query_parser(request['request_target'])

	for hdr in req_header:
		key = hdr[0:hdr.index(':')].lower()
		value = hdr[hdr.index(':')+1:].strip().lower()
		request[key] = value

	if request['request_target'] == '/':
		request['request_target'] = '/index.html'

	return request


async def request_handler(reader, writer):

	try:
		header = await reader.readuntil(b'\r\n\r\n')
		header = header.decode().split('\r\n\r\n')[0]
		request = request_parser(header)
		if 'content-length' in request:
			con_len = int(request['content-length'])
			request['body'] = await reader.readexactly(con_len)
			# request['body'] = await reader.readuntil(b'\n')
			request['body'] = body_parser(request)
		
		print("Request: \n")
		pprint.pprint(request)		
		response = generate_response(request)
		print("Response: \n")
		pprint.pprint(response)		
		writer.write(response)
		await writer.drain()
		print("Closing connection")
		writer.close()

	except asyncio.streams.IncompleteReadError:
		pass


def start_server():
	loop = asyncio.get_event_loop()
	coro = asyncio.start_server(request_handler, host, port)
	server = loop.run_until_complete(coro)
	print("Serving on ", host, "port: ", port)
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		print("\nShutting Down Server...\n")
	finally:
		server.close()
		loop.run_until_complete(server.wait_closed())
		loop.close()


if __name__ == '__main__':
	start_server()
