import random

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