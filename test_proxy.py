import random
import requests

def get_random_proxy(proxies):
    """
    Randomly selects a proxy from the given list, parses it, and returns the proxy URL.

    :param proxies: List of proxies in the format `IP:PORT:USERNAME:PASSWORD`.
    :return: Proxy URL in the format `http://USERNAME:PASSWORD@IP:PORT`.
    """
    proxy = random.choice(proxies)
    ip, port, username, password = proxy.split(":")
    proxy_url = f"http://{username}:{password}@{ip}:{port}"
    return proxy_url

def test_proxy(proxy_url, test_url="http://httpbin.org/ip"):
    """
    Tests the given proxy by making a request to a test URL.

    :param proxy_url: Proxy URL in the format `http://USERNAME:PASSWORD@IP:PORT`.
    :param test_url: URL to test the proxy (default is `http://httpbin.org/ip`).
    :return: Response status and data if successful, or an error message.
    """
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=10)
        response.raise_for_status()
        return response.status_code, response.json()
    except requests.RequestException as e:
        return "Error", str(e)

# Example usage
if __name__ == "__main__":
    proxy_list = [
        "195.216.158.166:29842:kjasis:axQ6cnwT",
        "195.216.158.94:29842:kjasis:axQ6cnwT",
    ]

    # selected_proxy = get_random_proxy(proxy_list)
    # print(f"Using proxy: {selected_proxy}")

    status, result = test_proxy(proxy_list[1])
    print(f"Test result: Status = {status}, Data = {result}")
