import socket
import struct

# Table 1 - Domain names and corresponding IP addresses
DOMAIN_IP_MAP = {
    "google.com": ["192.165.1.1", "192.165.1.10"],
    "youtube.com": ["192.165.1.2"],
    "uwaterloo.ca": ["192.165.1.3"],
    "wikipedia.org": ["192.165.1.4"],
    "amazon.ca": ["192.165.1.5"]
}

def handle_dns_query(query):
    """Handle incoming DNS query and generate response."""
    header = struct.unpack('!HHHHHH', query[:12])
    qname, offset = read_name(query, 12)
    qtype, qclass = struct.unpack('!HH', query[offset:offset + 4])

    # Construct DNS response
    if qname not in DOMAIN_IP_MAP:
        # Return NXDOMAIN response if domain is not found
        header_response = struct.pack('!HHHHHH', header[0], 0x8183, 0x0001, 0x0000, 0x0000, 0x0000)
        return header_response + query[12:]

    # Set the TTL based on the domain
    ttl = 260 if qname == "google.com" else 160 # As defined in lab manual

    # Normal response
    header_response = struct.pack('!HHHHHH', header[0], 0x8180, 0x0001, len(DOMAIN_IP_MAP[qname]), 0x0000, 0x0000)
    qname_response = b''.join(struct.pack('B', len(part)) + part.encode() for part in qname.split('.')) + b'\x00'
    answer_section = b''

    for ip_address in DOMAIN_IP_MAP[qname]:
        answer_section += qname_response
        answer_section += struct.pack('!HHIH', 0x0001, 0x0001, ttl, 4)  # Type A, Class IN, TTL, RDLENGTH
        answer_section += b''.join(int(b).to_bytes(1, 'big') for b in ip_address.split('.'))

    return header_response + query[12:] + answer_section


def read_name(message, offset):
    """Decode a DNS name.
    
    The DNS name is decoded by reading length-prefixed labels until a zero-length
    label is encountered, which marks the end of the name. Each label is decoded
    and joined with dots to form the full domain name."""
    parts = []
    while True:
        length = message[offset]
        if length == 0:
            return '.'.join(parts), offset + 1
        offset += 1
        parts.append(message[offset:offset + length].decode())
        offset += length

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('127.0.0.1', 10000))
        print("Server listening on port 10000...")
        while True: # Infinite loop until user decides to quit
            query, addr = sock.recvfrom(4096)
            response = handle_dns_query(query)
            sock.sendto(response, addr)
            print(f"Request:\n{' '.join([f'{b:02x}' for b in query])}")
            print(f"Response:\n{' '.join([f'{b:02x}' for b in response])}")

if __name__ == "__main__":
    main()
