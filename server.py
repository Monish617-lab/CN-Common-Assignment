import socket
import threading

HOST = "0.0.0.0"
TCP_PORT = 5000
UDP_PORT = 5001
BUFFER = 1024


def handle_tcp_client(conn, addr):
    print("[TCP] Connection established with %s:%d" % addr)
    try:
        while True:
            data = conn.recv(BUFFER)
            if not data:
                break
            client_id, _, message = data.decode().partition("|")
            if message.upper() == "EXIT":
                conn.sendall(b"ACK|Connection closing")
                break
            print("[TCP] Received from %s %s : %s" % (client_id, addr, message))
            conn.sendall(("ACK|" + message).encode())
    except ConnectionResetError:
        pass
    finally:
        conn.close()
        print("[TCP] Connection closed with %s:%d" % addr)


def tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, TCP_PORT))
    sock.listen(5)
    print("TCP server listening on port", TCP_PORT)
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_tcp_client,
                         args=(conn, addr), daemon=True).start()


def udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, UDP_PORT))
    print("UDP server listening on port", UDP_PORT)
    while True:
        data, addr = sock.recvfrom(BUFFER)
        client_id, _, message = data.decode().partition("|")
        print("[UDP] Received from %s %s : %s" % (client_id, addr, message))
        sock.sendto(("ACK|" + message).encode(), addr)


if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_server, daemon=True).start()
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("Server stopped")
