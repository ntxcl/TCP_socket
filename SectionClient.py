import sys, errno
from socket import *
import hashlib

PORT = 7037
serverName = "127.0.0.1"
SIZE_1_KiB = 1024
SIZE_32_KiB = 32 * SIZE_1_KiB

MAX_TCP_PAYLOAD = 65507

class Section:
    MAX_SECTION_SIZE = SIZE_32_KiB

    def __init__(self, num, size, digest):
        self.num = int(num)
        self.size = int(size)
        self.digest = digest
        self.from_byte = self.num * self.MAX_SECTION_SIZE
        self.to_byte = (self.num + 1) * self.MAX_SECTION_SIZE

def usage(program):
   sys.exit(f'Usage: python3 {program} HOST[:PORT] FILE')

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

def parse_address(addr):
    components = addr.split(':', maxsplit=1)
    hostname = components[0]
    port = PORT if len(components) == 1 else int(components[1])

    return (hostname, port)

def repeatRequest(section, clientSocket, hostname, port):
    msg=f'SECTION {section.num}'
    nummsg=0;
    data=''.encode()
    while(True):
        
        try:
            clientSocket.send(msg.encode())
            data=clientSocket.recv(section.size)
        except:
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((hostname, port))

        size=len(data)
        digest=md5(data)
        string=True

        try:
            data.decode()
            print("decoded data")
        except:
            string=False
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((hostname, port))

        if size==0:
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((hostname, port))
            # clientSocket.setblocking(0)
            # return repeatRequest(section, clientSocket, hostname, port)
        elif string and data.decode().startswith("ERROR:"):
            print(data.decode())
            print("received ERROR repeating request")
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((hostname, port))
            # return repeatRequest(section, clientSocket, hostname, port)
        elif section.size!=size:
            print(f'expected {section.size} was {size}\n repeating request')
            # return repeatRequest(section, clientSocket, hostname,port)
        elif section.digest!=digest:
            print(f'expected {section.digest} was {digest}\n repeating request')
            #return repeatRequest(section, clientSocket, hostname,port)
        
        else:
            print(f'ok')
            return data

def main(address, filename):
    hostname, port = parse_address(address)

    #request "LIST"
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((hostname, port))
    clientSocket.send("LIST".encode())
    response = clientSocket.recv(MAX_TCP_PAYLOAD)
    expected_file_digest, sections, total_size = list_sections(response)
    print(response.decode())
    clientSocket.close()

    #request for "SECTION"
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((hostname, port))
    #clientSocket.setblocking(0)
    file_contents = bytearray(total_size)

    # for section in sections:
    #     print(f"section={section.num}")

    for section in sections:
        
        # digest = -1
        # data = "ERROR"
        print(f"requesting {section.num}...")
        data=repeatRequest(section, clientSocket, hostname, port)

# while  digest != section.digest or data.startswith('ERROR'.encode()) :
#             msg=f"SECTION {section.num}"
#             print(msg)
#             clientSocket.send(msg.encode())
#             data = clientSocket.recv(section.size)
#             size = len(data)
#             digest = md5(data)

        # if size != section.size:
        # 	print(f'size {size}, expected {section.size}')
        # el
        # if digest != section.digest:
        # 	print(f'digest {digest}, expected {section.digest}')
        # else:
        # if digest == section.digest:
        file_contents[section.from_byte:section.to_byte] = data 
            # print(f"ok data for {section.num}")
        
    file_digest = md5(file_contents)
    if file_digest != expected_file_digest:
        print(f'{filename}: digest {file_digest}, expected {expected_file_digest}')
    else:
        with open (filename, 'wb') as f:
            f.write(file_contents)
        print("SUCESS")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage(sys.argv[0])

    sys.exit(main(*sys.argv[1:]))
