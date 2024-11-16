import socket

DNS_TABLE = {
    "google.com": ["192.165.1.1", "192.165.1.10"],
    "youtube.com": ["192.165.1.2"],
    "uwaterloo.ca": ["192.165.1.3"],
    "wikipedia.org": ["192.165.1.4"],
    "amazon.ca": ["192.165.1.5"],
}

def build_response(query):
    transaction_id = query[:2]
    flags = b'\x84\x00'
    questions = query[4:6]
    answers = len(DNS_TABLE.get("google.com", [])).to_bytes(2, 'big')
    additional = b'\x00\x00'
    response = transaction_id + flags + questions + answers + additional
    # Add answer sections
    return response

def main():
    HOST, PORT = '127.0.0.1', 10053
    print(str(PORT) + "\n")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        while True:
            query, addr = server_socket.recvfrom(512)            
            # Format the query to display it as octets (space between every 2 characters)
            query_octets = ' '.join(f'{byte:02x}' for byte in query)
            print("Request:", query_octets)

            response = build_response(query)
            # Format the response to display it as octets (space between every 2 characters)
            response_octets = ' '.join(f'{byte:02x}' for byte in response)
            print("Response:", response_octets)
            server_socket.sendto(response, addr)

if __name__ == "__main__":
    main()
