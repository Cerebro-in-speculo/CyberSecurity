import socket
import sys

# Проверяем, передан ли аргумент командной строки
if len(sys.argv) < 2:
    print("Использование: python3 pythonfile.py <ip_или_хост>")
    sys.exit()

target = sys.argv[1]

# В Python 3 range работает как генератор по умолчанию
ports = range(1, 9000)

for port in ports:
    try:
        # Создаем объект сокета
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Устанавливаем тайм-аут, чтобы сканирование не длилось вечно
        sock.settimeout(0.5)
        
        # connect_ex возвращает 0 при успешном подключении
        result = sock.connect_ex((target, port))
        
        if result == 0:
            print("[+] Port {0} is Opened".format(port))
        else:
            print("[!] Port {0} is Closed".format(port))
            
        sock.close()
        
    except socket.error:
        print("[!] Error with socket!")
        sys.exit()
    except KeyboardInterrupt:
        print("\n[!] Сканирование остановлено пользователем.")
        sys.exit()