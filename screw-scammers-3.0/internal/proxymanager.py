import os, json, requests, random
from internal.util.colors import Fore
from internal.util.simpleprogbar import progbar

class ProxyManager:
    def __init__(self, file: str = 'config/data/proxies.txt', prompt_if_empty: bool = True):
        self._file = file
        self._prompt_if_empty = prompt_if_empty
        
        self._proxies: list[str]
        if os.path.exists(file):
            self._proxies = self._load_proxies()
        else:
            self._proxies = self._prompt_and_load()
            if not self._proxies:
                print(f"{Fore.RED}ERROR{Fore.RESET}: No proxies found")
                exit(1)

        print(f"{Fore.GREEN}SUCCESS{Fore.RESET}: ProxyManager initialized with {Fore.YELLOW}{len(self._proxies):,}{Fore.RESET} proxies")

    def _load_proxies(self) -> list[str]:
        with open(self._file, 'r') as f:
            proxies = f.read().splitlines()

        if not proxies and self._prompt_if_empty:
            print(f"{Fore.RED}ERROR{Fore.RESET}: No proxies found in {self._file}")
            exit(1)

        return proxies

    def _prompt_and_load(self) -> list[str] | None:
        if input(f"{Fore.YELLOW}WARNING{Fore.RESET}: No proxies found in '{self._file}', would you like to try and automatically fetch some? (y/n)").lower() != 'y':
            return None
        
        if not os.path.exists('config/dev-config.json'):
            print(f"{Fore.RED}ERROR{Fore.RESET}: Required file 'config/dev-config.json' not found")
            exit(1)

        with open('config/dev-config.json', 'r') as f:
            config = json.load(f)
        
        proxies: list[str] = []
        
        for host in progbar(config['proxy_sources']):
            response = requests.get(host)
            if response.status_code == 200:
                proxies.extend([proxy.rstrip() for proxy in response.text.splitlines()])

        proxies = list(set(proxies))
        if not proxies:
            print(f"{Fore.RED}ERROR{Fore.RESET}: Unable to fetch proxies from any sources")
            return None
        
        with open(self._file, 'w') as f:
            f.write('\n'.join(proxies))
        
        return proxies

    def get_random_proxy(self) -> str | None:
        return random.choice(self._proxies) if self._proxies else None
    
    def get_all_proxies(self) -> list[str]:
        return self._proxies
    
    def remove_proxy(self, proxy: str):
        self._proxies.remove(proxy)
        with open(self._file, 'w') as f:
            f.write('\n'.join(self._proxies))
        
if __name__ == '__main__':
    ProxyManager()