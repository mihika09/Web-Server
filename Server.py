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
	print("Hey")
	ROUTES[method][route] = controller


def route_handler(request, response):

	method = request['method']
	controller = request["request_target"]

	if controller in ROUTES[method]:
		response['body'] = ROUTES[method][controller](request, response)
		response['body'] = str(response['body']).encode()
		response = response_200_ok(response) + response['body']
		return response

	return None


def generate_encoded_response(response):

	pprint.pprint(response)
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
			# file.close()

			response['body'] = content
			response['header']['Content-Type'] = mimetypes.guess_type(request['request_target'])[0]
			response = response_200_ok(response) + response['body']
			return response

		except FileNotFoundError:
			return None

	return None


def generate_response(request):

	response = {'header': {}}
	# response['header'] = {}

	returned_response = static_file_handler(request, response)
	if returned_response is None:
		returned_response = route_handler(request, response)
		if returned_response is None:
			returned_response = response_404_not_found(response)

	response = returned_response
	return response


def body_parser(request):

	if request['content-type'] == 'text/plain':
		request['body'] = str(request['body'])

	elif request['content-type'] == 'application/json':
		request['body'] = json.loads(request['body'])

	return request['body']


def query_parser(request):

	path, query = request.split("?")
	q = dict(a.split("=") for a in query.split("&"))
	return path, q


def request_parser(header_stream):
	req_line, *req_header = header_stream.split('\r\n')
	request = dict(zip(['method', 'request_target', 'http_version'], req_line.split()))

	if '?' in request['request_target']:
		request['request_target'], request['query_content'] = query_parser(request)

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
			request['body'] = body_parser(request)

		print("##############Request##############\n", request)
		response = generate_response(request)
		writer.write(response)
		await writer.drain()
		print("Close the client socket")
		writer.close()

	except asyncio.streams.IncompleteReadError:
		print("Bad Request!")


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
