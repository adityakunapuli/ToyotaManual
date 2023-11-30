import re
import warnings
from urllib import parse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from config import *
from make_driver import driver
from utils import click_link, countdown_timer, reheat_navigation_soup

warnings.simplefilter('ignore')


def strip_query_from_url(asset_url):
    asset_url = asset_url.split('?')[0]
    parsed = parse.urlparse(asset_url)
    parsed = parsed._replace(query='', params='')
    asset_url = parse.urlunparse(parsed)
    return asset_url


def convert_url_to_local_path(asset_url):
    """
    Converts a http url into a local path based on the BASE_PATH provided above.
    If file already exists, then returns None (which is then used to bypass
     reqs.body.response)
    """
    asset_url = str(asset_url)
    asset_url = strip_query_from_url(asset_url)
    file_name = BASE_PATH / asset_url.replace(BASE_URL, '').lstrip('/')
    # don't re-download files and don't download files without extensions
    if file_name.exists() or '.' not in asset_url.split('/')[-1]:
        return None
    file_name.parent.mkdir(parents=True, exist_ok=True)
    return file_name


def parse_title(title, suffix='.html'):
    title = title.replace('/', '-')
    title = title.title()
    title = title.replace(': ', '/')
    title = re.sub(r';.*', '', title)
    title = title.replace('Ecu', 'ECU')
    if suffix:
        title += suffix
    return title


def download_pages(category):
    soup = reheat_navigation_soup()
    pages = soup.find_all(attrs={'src': ICON_PAGE})
    pages = [page.find_parent('a') for page in pages]
    failed_pages = []
    for page in tqdm(pages):
        a_id = page.get('id')
        try:
            click_link(elem_id=a_id)
            countdown_timer(1, silent=True)
            download_page(category=category)
        except Exception as e:
            failed_pages.append(a_id)
        finally:
            driver.switch_to.default_content()
            driver.switch_to.frame('navigation_frame')
    return failed_pages


def download_page(category):
    """
    Downloads CSS, images, etc
    """
    driver.switch_to.default_content()
    driver.switch_to.frame('manual_frame')
    page_source = driver.page_source
    soup = BeautifulSoup(page_source)
    table = soup.find('table', attrs={'class': 'side'}).text.replace('\xa0', '')
    doc_id = re.findall('Doc ID: (\w+)', table)[0]
    title = re.findall('Title: (.*)', table)[0]
    file_name = parse_title(title)
    file_name = str(Path(category.replace('/', '-')) / file_name)
    file_name = file_name.replace('.', f' ({doc_id}).')
    parents = len(Path(file_name).parents) - 1
    page_source = page_source.replace('/t3Portal', '../' * parents + 't3Portal')
    # page_url = f'https://techinfo.toyota.com/t3Portal/document/rm/RM30G0U/xhtml/{doc_id}.html'
    file_name = convert_url_to_local_path(file_name)
    if file_name:
        with open(file_name, 'w') as f:
            f.write(page_source)

    # driver.refresh()
    reqs = driver.requests
    unique_reqs = {}
    for req in reqs:
        if any([req.url.startswith(BASE_URL + '/t3Portal') is False,
                f'html' in req.url
                ]):
            continue
        req.url = strip_query_from_url(req.url)
        unique_reqs[req.url] = req
    unique_reqs = list(unique_reqs.values())

    for req in unique_reqs:
        if f'{BASE_URL}/t3Portal/document' in req.url and req.url.endswith('png'):
            file_name = convert_url_to_local_path(req.url)
            if file_name:
                # session = requests.Session()
                # session.max_redirects = 20
                try:
                    response = requests.get(url=req.url,
                                            headers=dict(req.headers),
                                            allow_redirects=True,
                                            verify=False,
                                            timeout=5
                                            )
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                except Exception as e:
                    print(f'Timed out for {file_name}')
        else:
            file_name = convert_url_to_local_path(req.url)
            if file_name:
                with open(file_name, 'wb') as f:
                    f.write(req.response.body)
