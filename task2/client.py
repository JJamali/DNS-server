import socket
import random


def build_query(domain_name):
    transaction_id = random.randint(0, 65535).to_bytes(2, 'big')
    flags = b'\x01\x00'
    questions = b'\x00\x01'
    additional = b'\x00\x00'
    qname = b''.join(len(part).to_bytes(1, 'big') + part.encode() for part in domain_name.split('.')) + b'\x00'
    qtype = b'\x00\x01'
    qclass = b'\x00\x01'
    return transaction_id + flags + questions + additional + qname + qtype + qclass

def main():
    HOST, PORT = '127.0.0.1', 10053
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        while True:
            domain_name = input("Enter Domain Name: ").strip()
            if domain_name == "end":
                print("Session ended")
                break
            query = build_query(domain_name)
            client_socket.sendto(query, (HOST, PORT))
            response, _ = client_socket.recvfrom(512)
            response_octets = ' '.join(f'{byte:02x}' for byte in response)
            print("Response:", response_octets)

if __name__ == "__main__":
    main()
