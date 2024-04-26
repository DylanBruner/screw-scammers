import os, time, random, requests
from internal.requestparser import RequestParser
from internal.util.colors import Fore
from internal.constants import REQUIRED_FILES
from internal.proxymanager import ProxyManager
from threading import Thread

no_proxy_mode = False

proxy_manager: ProxyManager = None
user_agents: list[str] = None
request_parser: RequestParser = None

# stats
total_requests = 0
failed_requests = 0

def main():
    global proxy_manager, user_agents, no_proxy_mode, request_parser

    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            print(f"{Fore.RED}ERROR{Fore.RESET}: Required file {file} not found")
            exit(1)

    THREAD_COUNT = int(input(f"{Fore.BLUE}Enter the number of threads to use {Fore.WHITE}({Fore.YELLOW}default 10{Fore.RESET}): {Fore.RESET}") or 10)
    
    print()

    try:
        request_parser = RequestParser('config/request.json')
    except Exception as e:
        print(f"{Fore.RED}ERROR{Fore.RESET}: Failed to parse request: {e}")
        exit(1)

    print(f"{Fore.GREEN}SUCCESS{Fore.RESET}: Request parsed successfully")

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

    print(f"{Fore.GREEN}SUCCESS{Fore.RESET}: Starting {Fore.YELLOW}{THREAD_COUNT:,}{Fore.RESET} threads...", end='')

    for _ in range(THREAD_COUNT):
        Thread(target=worker, daemon=True).start()

    print("done")
        

    print()

    while True:
        print(f"\r{Fore.CYAN}INFO{Fore.RESET}: Total requests: {Fore.YELLOW}{total_requests:,}{Fore.RESET} | Failed requests: {Fore.RED}{failed_requests:,}{Fore.RESET} | Proxies: {Fore.YELLOW}{len(proxy_manager.get_all_proxies()):,}{Fore.RESET}", end='')
        time.sleep(1)

def worker():
    for x in range(1):
        proxy = proxy_manager.get_random_proxy()
        proxy = {'http': f"http://{proxy}", 'https': f"https://{proxy}"} if proxy else {}
        if not proxy and not no_proxy_mode:
            print(f"{Fore.RED}ERROR{Fore.RESET}: No proxies found, exiting thread")
            return

        user_agent = random.choice(user_agents)

        request = request_parser.make_request()
        request.headers['User-Agent'] = user_agent

        session = requests.Session()
        session.proxies.update(proxy)

        try:
            preq = request.prepare()
            response = session.send(preq)

        # catch proxy errors
        except requests.exceptions.ProxyError as e:
            proxy_manager.remove_proxy(proxy['http'].split('//')[1])
            continue

        except Exception as e:
            global failed_requests
            failed_requests += 1
            print(f"\n{Fore.RED}ERROR{Fore.RESET}: {e}")
            continue

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}ERROR{Fore.RESET}: Keyboard interrupt detected, exiting")
        exit(1)