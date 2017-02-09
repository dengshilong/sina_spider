import click
import urllib.request
from bs4 import BeautifulSoup
import logging

old_urls = set()
LOGGER = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)


def get_repsonse(url):
    """
    Simple dict but also support access as x.y style.

    >>> response = get_repsonse('')
    >>> response
    """
    try:
        response = urllib.request.urlopen(url).read()
        return response
    except Exception as e:
        logging.warning('get response error {}'.format(e))
        return None

def get_all_urls(response):
    """
    >>> response = 'sfsd<a href="http://www.bai.com">sdfs</a>'
    >>> urls = get_all_urls(response)
    >>> urls
    ['http://www.bai.com']
    """
    soup = BeautifulSoup(response, 'html.parser')
    urls = []
    for link in soup.find_all('a'):
        urls.append(link.get('href'))
    return urls


def save_url(url, response):
    pass


def spider(url, deep):
    if url in old_urls or deep == 0:
        return
    print(url)
    LOGGER.info('crawling {}'.format(url))
    response = get_repsonse(url)
    if not response:
        return
    save_url(url, response)
    old_urls.add(url)
    urls = get_all_urls(response)
    for u in urls:
        spider(u, deep - 1)

def process_log(file, level):
    handler = logging.FileHandler(filename=file)
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    if level <= 1:
        LOGGER.setLevel(logging.DEBUG)
    elif level == 2:
        LOGGER.setLevel(logging.INFO)
    elif level == 3:
        LOGGER.setLevel(logging.WARNING)
    elif level == 4:
        LOGGER.setLevel(logging.ERROR)
    else:
        LOGGER.setLevel(logging.CRITICAL)
    return LOGGER


@click.command()
@click.option('--url', '-u', help='seed url')
@click.option('--deep', '-d', default=1,
              help='crawl deep')
@click.option('--file', '-f', default='spider.log',
              help='log file')
@click.option('--level', '-l', default=1,
              help='log level')
@click.option('--testself', is_flag=True)
def main(url, deep, file, level, testself):
    if testself:
        import doctest
        doctest.testmod()
        return
    process_log(file, level)
    spider(url, deep)


if __name__ == "__main__":
    main()