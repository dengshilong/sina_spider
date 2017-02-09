import click
import urllib.request
from bs4 import BeautifulSoup


old_urls = set()


def get_repsonse(url):
    try:
        response = urllib.request.urlopen(url).read()
        return response
    except Exception as e:
        print(e)

def get_all_urls(response):
    soup = BeautifulSoup(response, 'html.parser')
    urls = []
    for link in soup.find_all('a'):
        urls.append(link.get('href'))
    return urls


def save_url(url, response):
    pass


def _spider(url, deep):
    if url in old_urls or deep == 0:
        return
    print(url)
    response = get_repsonse(url)
    if not response:
        return
    save_url(url, response)
    old_urls.add(url)
    urls = get_all_urls(response)
    print(urls)
    for u in urls:
        _spider(u, deep - 1)


@click.command()
@click.option('--url', '-u', help='seed url')
@click.option('--deep', '-d', default=1,
              help='crawl deep')
def spider(url, deep):
    _spider(url, deep)


if __name__ == "__main__":
    spider()