import os, time
from internal.util.colors import Fore
from internal.constants import REQUIRED_FILES
from internal.proxymanager import ProxyManager
from threading import Thread

no_proxy_mode = False

proxy_manager: ProxyManager = None
user_agents: list[str] = None

# stats
total_requests = 0
failed_requests = 0

def main():
    global proxy_manager, user_agents, no_proxy_mode

    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            print(f"{Fore.RED}ERROR{Fore.RESET}: Required file {file} not found")
            exit(1)

    THREAD_COUNT = int(input(f"{Fore.BLUE}Enter the number of threads to use {Fore.WHITE}({Fore.YELLOW}default 10{Fore.RESET}): {Fore.RESET}") or 10)
    
    print()

    proxy_manager = ProxyManager()

    if not proxy_manager.get_all_proxies():
        if input(f"{Fore.YELLOW}WARNING{Fore.RESET}: No proxies found, would you like to continue without using proxies? (y/n)").lower() != 'y':
            exit(0)
        no_proxy_mode = True

    with open('config/data/user-agents.txt', 'r') as f:
        user_agents = [ua.rstrip() for ua in f.read().splitlines() if ua.strip()]
    if not user_agents:
        print(f"{Fore.RED}ERROR{Fore.RESET}: No user agents found")
        exit(1)

    print(f"{Fore.GREEN}SUCCESS{Fore.RESET}: UserAgents loaded: {Fore.YELLOW}{len(user_agents):,}{Fore.RESET}")

    print(f"{Fore.GREEN}SUCCESS{Fore.RESET}: Starting {Fore.YELLOW}{THREAD_COUNT}{Fore.RESET} threads")

    for _ in range(THREAD_COUNT):
        Thread(target=worker, daemon=True).start()
        
    print(f"{Fore.GREEN}SUCCESS{Fore.RESET}: Threads started")

    print()

    while True:
        print(f"\r{Fore.CYAN}INFO{Fore.RESET}: Total requests: {Fore.YELLOW}{total_requests:,}{Fore.RESET} | Failed requests: {Fore.RED}{failed_requests:,}{Fore.RESET} | Proxies: {Fore.YELLOW}{len(proxy_manager.get_all_proxies()):,}{Fore.RESET}", end='')
        time.sleep(1)

def worker():
    while True:
        proxy = proxy_manager.get_random_proxy() or {}
        if not proxy and not no_proxy_mode:
            print(f"{Fore.RED}ERROR{Fore.RESET}: No proxies found, exiting thread")
            return
        
        time.sleep(1)
        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}ERROR{Fore.RESET}: Keyboard interrupt detected, exiting")
        exit(1)