#!/usr/bin/env python3

import socket
import sys

def send_file(filename, server="localhost", port=9100, chunk_size=32):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))
    print("connected to %s:%d" % (server, port))

    with open(filename, "rb") as test_file_handle:
        data = test_file_handle.read()
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        print("sending %d chunks" % len(chunks))

        for chunk in chunks:
            client.send(chunk)

    client.close()

if __name__ == "__main__":
    if not (2 <= len(sys.argv) <= 4):
        print("usage: %s FILE [SERVER PORT]" % sys.argv[0])
        print("send a pcl (or any other) file via a socket in 32 bytes chunks")
        print()
        print("\tFILE a file")
        print("\tSERVER defaults to localhost")
        print("\tPORT defaults to 9100")
        exit(1)

    sys.argv += ["localhost", "9100"]

    filename = sys.argv[1]
    server = sys.argv[2]
    port = int(sys.argv[3])

    send_file(filename, server, port)