import queue
import threading
from collections import namedtuple

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

Website = namedtuple('Website', ['url', 'deep', 'max_deep'])

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


def do_work(item, q):
    LOGGER.info("current thread {}".format(threading.current_thread().name))
    url = item.url
    if url in old_urls:
        return
    print(url)
    LOGGER.info('crawling {}, deep {} max_deep {}'.format(url, item.deep, item.max_deep))
    response = get_repsonse(url)
    if not response:
        return
    save_url(url, response)
    old_urls.add(url)
    if item.deep == item.max_deep:
        return
    urls = get_all_urls(response)
    for u in urls:
        q.put(Website(u, item.deep + 1, item.max_deep))

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


def worker(q):
    while True:
        item = q.get()
        if item is None:
            break
        do_work(item, q)
        q.task_done()

@click.command()
@click.option('--url', '-u', help='seed url')
@click.option('--deep', '-d', default=1,
              help='crawl deep')
@click.option('--file', '-f', default='spider.log',
              help='log file')
@click.option('--level', '-l', default=1,
              help='log level')
@click.option('--testself', is_flag=True)
@click.option('--thread', '-t', default=10,
              help='thread number')
def main(url, deep, file, level, testself, thread):
    if testself:
        import doctest
        doctest.testmod()
        return
    process_log(file, level)
    q = queue.Queue()
    threads = []
    for i in range(thread):
        t = threading.Thread(target=worker, args=(q,))
        t.start()
        threads.append(t)

    q.put(Website(url, 0, deep))
    # block until all tasks are done
    q.join()
    # stop workers
    for i in range(thread):
        q.put(None)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()