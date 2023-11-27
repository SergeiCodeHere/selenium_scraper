import requests
import logging
import json

from fp.fp import FreeProxy, FreeProxyException
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

FORMAT = '%(asctime)s : %(lineno)s : %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

PROXY_ENABLE = False

logging.info(f'Proxy status: {PROXY_ENABLE}')


def get_headers() -> dict[str, str]:
    ua = UserAgent().random

    headers = {
        'User-Agent': ua,
    }
    return headers


def get_proxy() -> dict[str, str] | None:
    try:
        ip = FreeProxy(timeout=0.3, https=True).get()
        proxy = {
            'http': ip,
            'https': ip
        }
        logging.info(f'Proxy received')
        return proxy
    except FreeProxyException as _ex:
        logging.info(f'Work without proxy. {_ex.message}')
        return None


def get_ip(headers: dict[str, str], proxy: dict[str, str] | None) -> str | None:
    cur_ip = None if proxy is None else proxy.get('https').split(':')[1]

    resp_2ip = requests.get('https://2ip.ru/', headers=headers, proxies=proxy)

    if resp_2ip.status_code == 200:
        soup = BeautifulSoup(resp_2ip.text, 'lxml')
        ip_addr = soup.find(id='d_clip_button').find('span').text
        if ip_addr == cur_ip:
            logging.info(f'Proxy works. Current ip address: {ip_addr}')
        else:
            logging.info(f'Proxy don\'t works. My ip address: {ip_addr}')
            cur_ip = ip_addr
    else:
        return None

    return cur_ip


def get_time_zone(headers: dict[str, str], proxy: dict[str, str] | None, cur_ip: str) -> str | None:
    with requests.Session() as geoip2:
        geoip2.proxies = proxy

        init_get = geoip2.get('https://www.maxmind.com/en/geoip2-precision-demo', headers=headers)

        if init_get.status_code == 200:

            soup = BeautifulSoup(init_get.text, 'lxml')
            crf_token = soup.find(id='content').find('script').text.split('\n')[2].split('"')[1]

            headers['X-Csrf-Token'] = crf_token
            headers['X-Requested-With'] = 'XMLHttpRequest'
            logging.info(f'Csrf Token received: {crf_token}')

            resp_token = geoip2.post('https://www.maxmind.com/en/geoip2/demo/token', headers=headers)

            if resp_token.status_code == 201:
                headers['Authorization'] = 'Bearer ' + resp_token.json()['token']

                information_ip = geoip2.get(f'https://geoip.maxmind.com/geoip/v2.1/city/{cur_ip}?demo=1',
                                            headers=headers)

                if information_ip.status_code == 200:
                    time_zone = information_ip.json()['location']['time_zone']
                    logging.info(f'Ip time_zone received: {time_zone}')
                else:
                    logging.info(f"Can't get time_zone")
                    return None
            else:
                logging.info(f"Can't get token")
                return None
        else:
            logging.info(f"Can't load www.maxmind.com")
            return None

    return time_zone


def get_cities(headers: dict[str, str], proxy: dict[str, str] | None, time_zone: str) -> None:
    with requests.Session() as get_city:
        get_city.proxies = proxy
        get_city.headers = headers

        get_all_cities = get_city.get('https://gist.github.com/salkar/19df1918ee2aed6669e2')

        if get_all_cities.status_code == 200:

            soup = BeautifulSoup(get_all_cities.text, 'lxml')

            cities = soup.find(
                class_='highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file')
            cities = cities.find_all(lambda tag: tag.name == 'td' and time_zone in tag.text)

            trans_table = str.maketrans({
                '\n': '',
                '[': '',
                ']': '',
                '"': ''
            })

            if cities:
                city_arr = []
                for city in cities:
                    city_arr.append(city.text.translate(trans_table).split(',')[0].strip())

            logging.info(f"Cities received: {', '.join(city_arr)}")

            with open('result_time_zone.txt', 'w', encoding='CP1251') as output_file:
                output_file.write(time_zone + '\n' + ', '.join(city_arr))
                logging.info(f"Success write!")
        else:
            logging.info(f"Can't get cities list")


def main():
    headers = get_headers()

    if PROXY_ENABLE:
        proxy = get_proxy()
    else:
        proxy = None

    cur_ip = get_ip(dict(headers), proxy)
    if cur_ip:
        time_zone = get_time_zone(dict(headers), proxy, cur_ip)

        if time_zone:
            get_cities(dict(headers), proxy, time_zone)


if __name__ == '__main__':
    main()
