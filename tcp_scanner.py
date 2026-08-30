#!/usr/bin/env python3
"""
Использование:
    python scanner.py <хост> [--ports ПОРТЫ] [--threads ПОТОКИ] [--timeout СЕК] [--verbose]
"""

import argparse
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional

# Цветной вывод
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def parse_port_range(port_spec: str) -> List[int]:
    """
    Преобразует строку с диапазоном портов в список целых чисел.
    Поддерживает форматы:
        - "80"           (один порт)
        - "80,443,8080" (список через запятую)
        - "1-1024"      (диапазон включительно)
        - "1-1024,8080" (комбинация)
    """
    ports = set()
    for part in port_spec.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.update(range(start, end + 1))
        else:
            ports.add(int(part))
    return sorted(ports)

def scan_port(host: str, port: int, timeout: float, verbose: bool = False) -> Optional[Tuple[int, bool]]:
    """
    Проверяет один TCP-порт.
    Возвращает (port, is_open) или None, если произошла ошибка (кроме таймаута).
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            if result == 0:
                if verbose:
                    print(f"{Colors.GREEN}[+] Port {port} is OPEN{Colors.RESET}")
                return (port, True)
            else:
                if verbose:
                    print(f"{Colors.RED}[!] Port {port} is CLOSED{Colors.RESET}")
                return (port, False)
    except socket.gaierror:
        # Ошибка разрешения имени хоста – критична для всех портов
        print(f"{Colors.RED}[!] Не удалось разрешить имя хоста: {host}{Colors.RESET}")
        sys.exit(1)
    except socket.error as e:
        # Другие ошибки (например, нехватка прав) – просто считаем порт закрытым
        if verbose:
            print(f"{Colors.YELLOW}[?] Port {port} error: {e}{Colors.RESET}")
        return (port, False)
    except Exception as e:
        if verbose:
            print(f"{Colors.YELLOW}[?] Port {port} unexpected error: {e}{Colors.RESET}")
        return (port, False)

def main():
    parser = argparse.ArgumentParser(
        description="Многопоточный TCP-сканер портов",
        epilog="Пример: python scanner.py example.com --ports 1-1000 --threads 50"
    )
    parser.add_argument("host", help="IP-адрес или доменное имя целевого хоста")
    parser.add_argument("-p", "--ports", default="1-2000",
                        help="Диапазон портов (по умолчанию: 1-2000). Форматы: 80, 1-1024, 80,443,8080")
    parser.add_argument("-t", "--threads", type=int, default=100,
                        help="Количество потоков (по умолчанию: 100)")
    parser.add_argument("--timeout", type=float, default=0.5,
                        help="Таймаут подключения в секундах (по умолчанию: 0.5)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Выводить также закрытые порты и ошибки")
    args = parser.parse_args()

    # 1. Разрешение имени хоста (с проверкой)
    try:
        target_ip = socket.gethostbyname(args.host)
        print(f"{Colors.GREEN}[*] Цель: {args.host} -> {target_ip}{Colors.RESET}")
    except socket.gaierror:
        print(f"{Colors.RED}[!] Ошибка: не удалось разрешить имя {args.host}{Colors.RESET}")
        sys.exit(1)

    # 2. Парсинг портов
    try:
        ports = parse_port_range(args.ports)
    except ValueError as e:
        print(f"{Colors.RED}[!] Неверный формат портов: {e}{Colors.RESET}")
        sys.exit(1)

    if not ports:
        print(f"{Colors.RED}[!] Список портов пуст.{Colors.RESET}")
        sys.exit(1)

    # Предупреждение о привилегированных портах (<1024)
    low_ports = [p for p in ports if p < 1024]
    if low_ports and sys.platform != 'win32':
        try:
            # Проверяем права, создав временный сокет на привилегированном порту
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(0.1)
            test_sock.bind(('', 1))
            test_sock.close()
        except socket.error:
            print(f"{Colors.YELLOW}[!] Внимание: для сканирования портов ниже 1024 могут потребоваться права root/администратора.{Colors.RESET}")

    print(f"[*] Сканирование {len(ports)} портов на {target_ip} с {args.threads} потоками (таймаут {args.timeout} с)")
    if args.verbose:
        print("[*] Режим VERBOSE: вывод всех портов")
    else:
        print("[*] Будут показаны только ОТКРЫТЫЕ порты. Для детального вывода используйте -v")

    # 3. Многопоточное сканирование
    open_ports = []
    closed_count = 0
    error_count = 0

    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            # Создаём задачи для всех портов
            future_to_port = {
                executor.submit(scan_port, target_ip, port, args.timeout, args.verbose): port
                for port in ports
            }

            # Обрабатываем результаты по мере завершения
            for future in as_completed(future_to_port):
                result = future.result()
                if result is not None:
                    port, is_open = result
                    if is_open:
                        open_ports.append(port)
                        if not args.verbose:
                            # В не-verbose режиме печатаем сразу при обнаружении
                            print(f"{Colors.GREEN}[+] Port {port} is OPEN{Colors.RESET}")
                    else:
                        closed_count += 1
                else:
                    error_count += 1

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Сканирование прервано пользователем. Ожидание завершения текущих потоков...{Colors.RESET}")
        executor.shutdown(wait=False)
        sys.exit(1)

    # 4. Итоговый вывод
    print("\n" + "=" * 50)
    print(f"{Colors.GREEN}[+] Сканирование завершено.{Colors.RESET}")
    print(f"    Открытых портов: {len(open_ports)}")
    if args.verbose:
        print(f"    Закрытых портов: {closed_count}")
        if error_count:
            print(f"    Ошибок: {error_count}")
    if open_ports:
        print(f"{Colors.GREEN}    Список открытых портов: {', '.join(map(str, open_ports))}{Colors.RESET}")
    else:
        print(f"{Colors.RED}    Открытых портов не найдено.{Colors.RESET}")
    print("=" * 50)

if __name__ == "__main__":
    main()