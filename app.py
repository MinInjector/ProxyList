import socket
import time

# --- CẤU HÌNH ---
IP = "0.0.0.0" 
PORT = 8080   
TIMEOUT = 10   # Giây

# Khởi tạo Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

# clients = { "Gamertag": {"addr": (IP, Port), "last_seen": timestamp} }
clients = {}

print("==========================================")
print("   MCPE VOICE CHAT SERVER - VERSION 2.0   ")
print("==========================================")
print(f"[*] Server IP: {socket.gethostbyname(socket.gethostname())}")
print(f"[*] Port: {PORT}")
print("------------------------------------------")

while True:
    try:
        data, addr = sock.recvfrom(4096)
        if not data: continue
        curr_time = time.time()

        # 1. XỬ LÝ PING (Mã 0xFE)
        if data[0] == 0xFE:
            # Dọn dẹp người chơi offline
            expired = [t for t, info in clients.items() if curr_time - info["last_seen"] > TIMEOUT]
            for t in expired:
                print(f"[-] {t} đã thoát (Timeout)")
                del clients[t]
            
            # Gửi phản hồi: [Mã 0xFE, Số người online]
            response = bytearray([0xFE, len(clients)])
            sock.sendto(response, addr)
            continue

        # 2. XỬ LÝ ÂM THANH
        try:
            tag_size = data[0]
            gamertag = data[1 : 1 + tag_size].decode('utf-8')
        except: continue

        # Thêm mới hoặc cập nhật Port cho người chơi
        if gamertag not in clients:
            print(f"[+] {gamertag} tham gia: {addr}")
        elif clients[gamertag]["addr"] != addr:
            print(f"[*] {gamertag} đổi mạng/port: {addr}")

        clients[gamertag] = {"addr": addr, "last_seen": curr_time}

        # 3. PHÁT ÂM THANH CHO NGƯỜI KHÁC (BROADCAST)
        for tag, info in clients.items():
            if tag != gamertag:
                try:
                    sock.sendto(data, info["addr"])
                except: pass

    except KeyboardInterrupt:
        print("\n[!] Dừng Server...")
        break
    except Exception as e:
        print(f"[X] Lỗi: {e}")

sock.close()
