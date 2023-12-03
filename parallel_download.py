import re
import warnings
from pathlib import PosixPath
from typing import Union
from urllib import parse

import ray
import requests
from lxml import etree as ET
from tqdm import tqdm

from config import *


def download_toc():
    toc_url = f'{BASE_URL}/t3Portal/external/en/rm/RM30G0U/toc.xml'
    xml = session.get(toc_url, verify=False)
    return xml


def get_toc_xml():
    xml = download_toc()
    tree = ET.fromstring(xml.content)
    root = tree.getroottree()
    items = root.findall(".//item[@href]")
    items = [item for item in items if item.attrib.get('href')]
    page_map = {}
    for item in items:
        href = item.attrib.get('href')
        if not href:
            continue
        page_title = item.find('name').text.strip()
        path = [x.find('name').text.strip() for x in item.iterancestors('item')][::-1]
        path.append(page_title)
        path = [x.replace('/', '-') for x in path]
        page_map[href] = path
    return page_map


def strip_query_from_url(asset_url):
    asset_url = asset_url.split('?')[0]
    parsed = parse.urlparse(asset_url)
    parsed = parsed._replace(query='', params='')
    asset_url = parse.urlunparse(parsed)
    return asset_url


def make_local_path(url: str) -> PosixPath:
    url = strip_query_from_url(url)
    local_path = BASE_PATH / url.replace('https://techinfo.toyota.com/', '')
    local_path.parent.mkdir(parents=True, exist_ok=True)
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
    session = requests.Session()
    session.post(AUTHENTICATION_URL, headers=AUTHENTICATION_HEADERS)
    toc = get_toc_xml()
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
