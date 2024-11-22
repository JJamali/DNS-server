import socket
import os
from datetime import datetime

def generate_headers(status_code, file_path=None):
    """
    Generate HTTP headers based on the status code and optional file path.
    """
    headers = {
        "Connection": "keep-alive", # Persistent HTML
        "Date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "Server": "SimplePythonHTTPServer",
    }
    if status_code == 200 and file_path:
        headers.update({
            "Last-Modified": datetime.utcfromtimestamp(os.path.getmtime(file_path)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "Content-Length": str(os.path.getsize(file_path)),
            "Content-Type": "text/html" if file_path.endswith(".html") else "application/octet-stream",
        })
    return headers

def handle_request(request):
    lines = request.splitlines()
    method, path, _ = lines[0].split()
    file_path = path.lstrip('/')
    if method not in ("GET", "HEAD"):    
        return 405, "Method Not Allowed", None
    if not os.path.exists(file_path):
        return 404, "File Not Found", None
    return 200, "OK", file_path

def serve_client(client_socket):
    """
    Handles an HTTP request from a client, generates an appropriate response, 
    and sends it back to the client.
    """
    request = client_socket.recv(1024).decode('utf-8')
    status, message, file_path = handle_request(request)
    headers = generate_headers(status, file_path)
    response = f"HTTP/1.1 {status} {message}\r\n" + "\r\n".join(f"{key}: {value}" for key, value in headers.items()) + "\r\n\r\n"
    client_socket.sendall(response.encode())
    if status == 200 and file_path:
        with open(file_path, 'rb') as f:
            client_socket.sendall(f.read())
    client_socket.close()

def main():
    HOST, PORT = '127.0.0.1', 6789
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"{PORT}\n")
        while True:
            client_socket, _ = server_socket.accept()
            serve_client(client_socket)

if __name__ == "__main__":
    main()
