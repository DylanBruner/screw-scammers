import json, os, requests
from internal.util.jsonutils import validate_path

class ParsedRequest:
    def __init__(self, host: str, method: str, headers: dict[str, str | int | float], cookies: list[str], payload: dict):
        self._host = host
        self._method = method
        self._headers = headers
        self._cookies = cookies
        self._payload = payload

    def __repr__(self):
        return f"ParsedRequest(host=\"{self._host}\", method=\"{self._method}\")"
    
class RequestParser:
    def __init__(self, file: str, entry_index: int = 0):
        self._file = file
        self._entry_index = entry_index # im not sure why the entry would ever need to be changed, but the option is there

        if not os.path.exists(file):
            raise FileNotFoundError(f"File {file} not found")
        
        self._parsed: ParsedRequest = self._parse(entry_index=entry_index)
    
    def _parse(self, entry_index: int) -> ParsedRequest:
        try:
            with open(self._file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON file")

        if not validate_path(f'log.entries.{entry_index}.request', data) or not validate_path(f'log.entries.{entry_index}.response', data):
            raise ValueError(f"Invalid file format, missing request/response data")
        
        entry = data['log']['entries'][entry_index]

        return ParsedRequest(
            host=entry['request']['url'],
            method=entry['request']['method'],
            headers={
                header['name']: header['value'] for header in entry['request']['headers']
            },
            cookies=entry['request']['cookies'],
            payload=entry['request']['postData'].get('params', [])
        )

    def make_request(self) -> requests.Request:
        return requests.Request(
            method=self._parsed._method,
            url=self._parsed._host,
            headers=self._parsed._headers,
            cookies=self._parsed._cookies,
            data=self._parsed._payload
        )

if __name__ == '__main__':
    parser = RequestParser('config/request.json')
    print(parser._parsed)
    print(parser._parsed._payload)
    req = parser.make_request()
    preq = req.prepare()

    requests.Session().send(preq)