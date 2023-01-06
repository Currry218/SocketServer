from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from os.path import exists

def GetRequest(client):
	request = ""
	client.settimeout(1)
	try:
		request = client.recv(1024).decode()
		while(request):
			request += client.recv(1024).decode()
	except socket.timeout:
		if not request: 
			print("Timeout, didn't receive any data!")
	finally:
		return request


def GetFileType(file_name):
	if ".html" in file_name:
		return "text/html"
	elif ".jpg" in file_name:
		return "image/jpeg"
	elif ".png" in file_name:
		return "image/png"
	elif ".css" in file_name:
		return "text/css"
	elif ".ico" in file_name:
		return "image/ico"
	else: return "text/plain"

def MovePage(client, file_name):
	header = "HTTP/1.1 301 Moved Permanently\r\nLocation: %s\r\n"%file_name
	client.sendall(bytes(header,"utf-8"))

def SetPage(client, file_name):
	if not(exists(file_name)): #ìf file doesn't exist
		print("Can't find", file_name)
		MovePage(client, "404.html")
	else:
		f = open(file_name, "rb")
		content = f.read()
		print("Sending", file_name, "\n")
  
		if file_name == "401.html":
			header = "HTTP/1.1 401 Unauthorized\r\n"
		elif file_name == "404.html":
			header = "HTTP/1.1 404 Not Found\r\n"
		else:
			header = "HTTP/1.1 200 OK\r\n"

		file_type = GetFileType(file_name)
		header += "Content-Length: %d\r\nContent-Type: %s\r\nConnection: close\r\n\r\n"%(len(content), file_type)
		header = header.encode() + content + "\r\n\r\n".encode()
		client.sendall(header)

def CheckPassword(client, request):
	if "uname=admin&psw=123456" in request:
		MovePage(client, "images.html")
	else:
		MovePage(client, "401.html")

def TakeRequest(client):
	while True:
		request = GetRequest(client)
		if not request:
			client.close()
			break
		if "POST" in request:
			CheckPassword(client, request)
   
		elif "GET" in request:
			#parse GET to get file name
			start = request.find("/")
			start += 1
			end = request.find(" HTTP")
			print(request[:end])
			file_name = request[start:end]
   
			if file_name == "": #/
				SetPage(client, "index.html")
			else:
				SetPage(client, file_name)

def WaitingConnection():
	while True:
		client, address = server.accept()
		print("\nClient", address ,"connected!")
		Thread(target = TakeRequest, args = (client,)).start()


host = ''
port = 8080
server = socket(AF_INET, SOCK_STREAM)
server.bind((host, port))

if __name__ == "__main__":
	try:
		server.listen(5)
		print("Listening on port",port)
		print("Waiting for Client...")
  
		thread_acpt = Thread(target = WaitingConnection)
		thread_acpt.start()
		thread_acpt.join()
	except:
		print("Error!!!")
	finally:
		server.close()