#!usr/bin/env python3

import os, sys, argparse
import requests as r
from bs4 import BeautifulSoup as bs
from progress.bar import Bar

JUSTIN_MALLER_URL = 'http://justinmaller.com'
WALLPAPERS_QUERY = '/wallpapers/'

parser = argparse.ArgumentParser(description='Download the wallpapers from justinmaller.com into the specified folder (./wallpapers by default)')
parser.add_argument('--output-path', help='The output path for the downloaded wallpapers', default='./wallpapers')
args = parser.parse_args()

def make_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as _:
        exit('[ERROR] The directory "{}" cannot be written.'.format(path))

def get_wallpaper_page_urls():
    res = r.get(JUSTIN_MALLER_URL + WALLPAPERS_QUERY)
    soup = bs(res.content, 'html.parser')
    anchors = soup.find_all("a", {'class': 'image'})
    urls = [anchor.get('href') for anchor in anchors]

    return urls

def get_wallpaper_urls(wallpaper_page_urls):
    for url in wallpaper_page_urls:
        res = r.get(JUSTIN_MALLER_URL + url)
        soup = bs(res.content, 'html.parser')
        images = soup.find_all('img')
        wallpaper_url = [image.get('src') for image in images if image.parent.get('id') == 'wallwindow'][0]
        filename =  wallpaper_url.rsplit('/', 1)[-1]

        yield (wallpaper_url, filename)

def download_wallpaper(url):
    res = r.get(url)
    return res.content

def save_wallpaper(data, file_path):
    f = open(file_path, 'wb')
    f.write(data)
    f.close()

def is_wallpaper_existing(file_path):
    return os.path.isfile(file_path)

def get_wallpapers(path):
    wallpaper_page_urls = get_wallpaper_page_urls()
    wallpaper_urls_iterator = get_wallpaper_urls(wallpaper_page_urls)

    print('{} wallpapers found. Let\'s download them all !'.format(len(wallpaper_page_urls)))

    bar = Bar('Downlading', max=len(wallpaper_page_urls))
    for i, url in enumerate(wallpaper_urls_iterator):
        setattr(bar, 'suffix' ,'%(index)d/%(max)d ({})'.format(url[1]))
        bar.next()

        file_path = '{}/{}'.format(path, url[1])
        if not is_wallpaper_existing(file_path):
            data = download_wallpaper(url[0])
            save_wallpaper(data, file_path)

    bar.finish()
    print('\nThose cute puppies are now available in {}. Enjoy :)'.format(path))

if __name__ == '__main__':
    make_dir(args.output_path)
    get_wallpapers(args.output_path)
