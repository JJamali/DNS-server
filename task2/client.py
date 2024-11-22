import socket
import struct
import random

# Helper functions
def create_dns_query(domain_name):
    """Construct the DNS query message."""
    random_id = random.randint(0, 65535)  # Generate a random 16-bit ID
    header = struct.pack('!HHHHHH', random_id, 0x0100, 0x0001, 0x0000, 0x0000, 0x0000)
    qname_parts = domain_name.split('.')
    qname = b''.join(struct.pack('B', len(part)) + part.encode() for part in qname_parts) + b'\x00'
    query = header + qname + struct.pack('!HH', 0x0001, 0x0001)  # Type A, Class IN
    return query

def parse_dns_response(response):
    """Parse the DNS response message."""
    header = struct.unpack('!HHHHHH', response[:12])
    answer_count = header[3]  # ANCOUNT
    offset = 12

    # Skip the question section
    while response[offset] != 0:
        offset += 1
    offset += 5  # Null byte + QTYPE + QCLASS

    # Parse the answer section
    answers = []
    for _ in range(answer_count):
        name, offset = read_name(response, offset)
        rtype, rclass, ttl, rdlength = struct.unpack('!HHIH', response[offset:offset + 10])
        offset += 10
        rdata = response[offset:offset + rdlength]
        offset += rdlength
        ip_address = '.'.join(str(b) for b in rdata)
        answers.append((name, rtype, rclass, ttl, ip_address))
    return answers

def read_name(message, offset):
    """Decode a DNS name."""
    parts = []
    while True:
        length = message[offset]
        if length == 0:
            return '.'.join(parts), offset + 1
        offset += 1
        parts.append(message[offset:offset + length].decode())
        offset += length

# Main client logic
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(('127.0.0.1', 10000))
        while True:
            domain_name = input("Enter Domain Name: ")
            if domain_name.lower() == "end": # End logic as defined in lab manual
                print("Session ended")
                break
            query = create_dns_query(domain_name)
            sock.send(query)
            response, _ = sock.recvfrom(4096)
            try:
                answers = parse_dns_response(response)
                for answer in answers:
                    print(f"{answer[0]}: type {answer[1]}, class {answer[2]}, TTL {answer[3]}, addr {answer[4]}")
            except Exception as e:
                print(f"Error parsing response: {e}")

if __name__ == "__main__":
    main()
