from email.utils import formatdate
import asyncio
import pprint
import mimetypes
host = '127.0.0.1'
port = 8888


def generate_encoded_response(response):

	pprint.pprint(response)
	enc_res = response['http_version']+" "+response['status']+'\r\n'
	for i, j in response['header'].items():
		enc_res = enc_res + i + ": " + j + "\r\n"

	enc_res = enc_res+'\r\n'
	enc_res = enc_res.encode()
	# print("Encoded response: \n")
	return enc_res


def add_response_headers(response):

	response['http_version'] = 'HTTP/1.1'
	response['header']['Date'] = formatdate(usegmt=True)
	response['header']['Connection'] = 'close'
	response = generate_encoded_response(response)
	return response


def response_404_not_found(response):

	response['status'] = '404 Not Found'
	response = add_response_headers(response)
	print("******Response Headers******\n\n", response)
	response['header']['Content-Length'] = str(0)
	print("******Response Headers******\n\n", response)
	response = generate_encoded_response(response)
	return response


def response_200_ok(response):

	response['status'] = '200 OK'
	if response['body']:
		response['header']['Content-Length'] = str(len(response['body']))

	response = add_response_headers(response)
	return response


def generate_static_response(request):

	response = {}

	filepath = '/Users/mallikamohta/Desktop/Mihika/Static' + request["request_target"]

	response['header'] = {}

	try:
		with open(filepath, 'rb') as file:
			content = file.read()
			# file.close()

		response['body'] = content
		response['header']['Content-Type'] = mimetypes.guess_type(request['request_target'])[0]
		response = response_200_ok(response) + response['body']
		# print("*******Response*******\n", response)

	except FileNotFoundError:
		response = response_404_not_found(response)

	return response

	# http_response = "HTTP/1.1 200 OK\r\n" + 'Content-Type:'+mimetype+'\r\n\r\n' + content + '\r\n'
	# return http_response.encode()


def request_parser(header_stream):
	req_line, *req_header = header_stream.split('\r\n')
	# print(req_line, "\n")
	request = dict(zip(['method', 'request_target', 'http_version'], req_line.split()))
	for hdr in req_header:
		key = hdr[0:hdr.index(':')].lower()
		value = hdr[hdr.index(':')+1:].strip().lower()
		request[key] = value

	if request['request_target'] == '/':
		request['request_target'] = '/index.html'

	return request


async def request_handler(reader, writer):
	header = await reader.readuntil(b'\r\n\r\n')
	header = header.decode().split('\r\n\r\n')[0]
	request = request_parser(header)
	if 'content_length' in request:
		con_len = request['content_length']
		request['body'] = await reader.readexactly(con_len)

	response = generate_static_response(request)
	print("###########Response##############\n", response)
	print(type(response))
	writer.write(response)
	await writer.drain()
	print("Close the client socket")
	writer.close()


def start_server():
	loop = asyncio.get_event_loop()
	coro = asyncio.start_server(request_handler, host, port)
	server = loop.run_until_complete(coro)

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
