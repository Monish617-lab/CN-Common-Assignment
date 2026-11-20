import socket
import time

BUFFER = 1024
TCP_PORT = 5000
UDP_PORT = 5001


def tcp_session(client_id, ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((ip, port))
    except OSError as err:
        print("Connection Status : Failed (%s)" % err)
        return
    print("Connection Status : Connected to %s:%d" % (ip, port))
    while True:
        message = input("Message Input : ")
        packet = ("%s|%s" % (client_id, message)).encode()
        start = time.perf_counter()
        sock.sendall(packet)
        try:
            reply = sock.recv(BUFFER)
        except socket.timeout:
            print("Acknowledgment Status : Not received")
            continue
        elapsed = (time.perf_counter() - start) * 1000
        print("Message Received : %s" % reply.decode().split("|", 1)[1])
        print("Acknowledgment Status : Received")
        print("Packet Transmission Time : %.3f ms" % elapsed)
        if message.lower() == "exit":
            break
    sock.close()
    print("Connection Status : Closed")


def udp_session(client_id, ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    print("Connection Status : Connectionless (no handshake)")
    while True:
        message = input("Message Input : ")
        packet = ("%s|%s" % (client_id, message)).encode()
        start = time.perf_counter()
        sock.sendto(packet, (ip, port))
        try:
            reply, _ = sock.recvfrom(BUFFER)
        except socket.timeout:
            print("Acknowledgment Status : Not received (packet may be lost)")
            continue
        elapsed = (time.perf_counter() - start) * 1000
        print("Message Received : %s" % reply.decode().split("|", 1)[1])
        print("Acknowledgment Status : Received")
        print("Packet Transmission Time : %.3f ms" % elapsed)
        if message.lower() == "exit":
            break
    sock.close()


def compare(client_id, ip, count=50):
    payload = "X" * 100

    tcp_times = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    t0 = time.perf_counter()
    sock.connect((ip, TCP_PORT))
    tcp_setup = (time.perf_counter() - t0) * 1000
    tcp_start = time.perf_counter()
    for i in range(count):
        t = time.perf_counter()
        sock.sendall(("%s|%s" % (client_id, payload)).encode())
        sock.recv(BUFFER)
        tcp_times.append((time.perf_counter() - t) * 1000)
    tcp_total = (time.perf_counter() - tcp_start) * 1000
    sock.sendall(("%s|EXIT" % client_id).encode())
    sock.recv(BUFFER)
    sock.close()

    udp_times = []
    lost = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    udp_start = time.perf_counter()
    for i in range(count):
        t = time.perf_counter()
        sock.sendto(("%s|%s" % (client_id, payload)).encode(), (ip, UDP_PORT))
        try:
            sock.recvfrom(BUFFER)
            udp_times.append((time.perf_counter() - t) * 1000)
        except socket.timeout:
            lost += 1
    udp_total = (time.perf_counter() - udp_start) * 1000
    sock.close()

    tcp_avg = sum(tcp_times) / len(tcp_times)
    udp_avg = sum(udp_times) / len(udp_times) if udp_times else 0

    print("\n========== TCP vs UDP Comparison Report ==========")
    print("%-32s %-16s %-16s" % ("Parameter", "TCP", "UDP"))
    print("-" * 66)
    print("%-32s %-16s %-16s" % ("Messages sent", count, count))
    print("%-32s %-16d %-16d" % ("Acknowledged", len(tcp_times), len(udp_times)))
    print("%-32s %-16d %-16d" % ("Lost", count - len(tcp_times), lost))
    print("%-32s %-16.4f %-16s" % ("Connection setup time (ms)", tcp_setup, "None"))
    print("%-32s %-16.4f %-16.4f" % ("Average time per message (ms)", tcp_avg, udp_avg))
    print("%-32s %-16.4f %-16.4f" % ("Total time (ms)", tcp_total, udp_total))
    print("%-32s %-16s %-16s" % ("Connection type", "Connection-based", "Connectionless"))
    print("%-32s %-16s %-16s" % ("Reliability", "Guaranteed", "Not guaranteed"))
    print("%-32s %-16s %-16s" % ("Ordering", "In order", "No ordering"))
    print("%-32s %-16s %-16s" % ("Header size", "20 bytes min", "8 bytes"))
    print("===================================================")


def main():
    client_id = input("Client ID : ")
    ip = input("Server IP Address : ")
    print("Protocol Selection : 1. TCP   2. UDP   3. Compare TCP and UDP")
    choice = input("Enter choice : ")
    if choice == "1":
        port = int(input("Port Number (5000) : ") or TCP_PORT)
        tcp_session(client_id, ip, port)
    elif choice == "2":
        port = int(input("Port Number (5001) : ") or UDP_PORT)
        udp_session(client_id, ip, port)
    elif choice == "3":
        compare(client_id, ip)
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
