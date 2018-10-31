import sys
from socket import *
import hashlib

PORT = 7037
serverName = "127.0.0.1"

SIZE_1_KiB = 1024
SIZE_32_KiB = 32 * SIZE_1_KiB

MAX_TCP_PAYLOAD = 65507

#def usage(program):
#    sys.exit(f'Usage: python3 {program} HOST[:PORT] FILE')

class Section:
    MAX_SECTION_SIZE = SIZE_32_KiB

    def __init__(self, num, size, digest):
        self.num = int(num)
        self.size = int(size)
        self.digest = digest
        self.from_byte = self.num * self.MAX_SECTION_SIZE
        self.to_byte = (self.num + 1) * self.MAX_SECTION_SIZE

def list_sections(response):
    #response = send_message('LIST', hostname, port)
    lines = response.decode().splitlines()

    file_digest = lines.pop(0)
    sections = set()
    total_size = 0

    for line in lines:
        columns = line.split(maxsplit=2)

        s = Section(*columns)
        sections.add(s)
        total_size += s.size

    return file_digest, sections, total_size


def md5(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

def send_message(message, hostname, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(message.encode(), (hostname, port))
        data, _ = s.recvfrom(MAX_TCP_PAYLOAD)

    return data

def main():

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, PORT))
    clientSocket.send("LIST".encode())
    response = clientSocket.recv(1024)
    print(response.decode())
    expected_file_digest, sections, total_size = list_sections(response)

    clientSocket.close()

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, PORT))
    file_contents = bytearray(total_size)

    for section in sections:
        digest = -1
        data = "ERROR"
        print(f"{section.num} {section.digest}")
        while data.startswith('ERROR') or digest!=section.digest:

        	clientSocket.send(f'SECTION {section.num}'.encode())
        	data = clientSocket.recv(section.size).decode()
        	size=len(data)
        	digest=md5(data.encode())

        if size != section.size:
        	print(f'size {size}, expected {section.size}')
        elif digest != section.digest:
        	print(f'digest {digest}, expected {section.digest}')
        else:
        	#file_contents[section.from_byte:section.to_byte] = data
        	print(f"ok data for {section.num}")

if __name__ == '__main__':
 #   if len(sys.argv) != 3:
  #      usage(sys.argv[0])

    sys.exit(main())