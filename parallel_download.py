import re
import warnings
from pathlib import PosixPath
from typing import Union
from urllib import parse

import ray
import requests
from tqdm import tqdm

from config import *
from utils import get_authenticated_session, get_toc_json


def strip_query_from_url(asset_url):
    asset_url = asset_url.split('?')[0]
    parsed = parse.urlparse(asset_url)
    parsed = parsed._replace(query='', params='')
    asset_url = parse.urlunparse(parsed)
    return asset_url


def make_local_path(url: str) -> PosixPath:
    url = strip_query_from_url(url)
    local_path = BASE_PATH / url.replace('https://techinfo.toyota.com/', '')
    local_path.tag.mkdir(parents=True, exist_ok=True)
    return local_path


def write_object(local_path: PosixPath, obj: Union[bytes, str]):
    if local_path.exists():
        return
    write_flag = 'w' if isinstance(obj, str) else 'wb'
    with open(local_path, write_flag) as f:
        f.write(obj)


def download_object(url):
    local_path = make_local_path(url)
    if local_path.exists():
        return
    obj = session.get(url, verify=False)
    write_object(local_path, obj.content)


def get_page(page: str):
    warnings.simplefilter('ignore')
    page_url = BASE_URL + page + '?sisuffix=ff&locale=en&siid=1701579734835'
    response = session.get(page_url, allow_redirects=True, verify=False)
    if response.text.startswith('<script>'):
        return page
    local_path = make_local_path(page_url)
    page_source = response.text
    page_source = page_source \
        .replace('https://techinfo.toyota.com', '') \
        .replace('/t3Portal', '../../../../../t3Portal')
    write_object(local_path=local_path, obj=page_source)
    url_queue = re.findall("(/t3Portal/[/\w\.\-]+)", response.text)
    if url_queue:
        url_queue = [BASE_URL + url for url in url_queue]
        for url in url_queue:
            if 'html' in url:
                # url = url.replace('https://techinfo.toyota.com', '')
                get_page(url)
            else:
                url = BASE_URL + url
                download_object(url)


if __name__ == '__main__':
    session = get_authenticated_session()
    toc = get_toc_json()
    pages = list(toc.keys())


    def to_iterator(obj_ids):
        while obj_ids:
            done, obj_ids = ray.wait(obj_ids)
            yield ray.get(done[0])


    get_page_remote = ray.remote(get_page)
    obj_ids = [get_page_remote.remote(page) for page in pages]
    failues = []
    for x in tqdm(to_iterator(obj_ids), total=len(obj_ids)):
        failues.append(x)
    print(failues)
