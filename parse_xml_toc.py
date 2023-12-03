# import xml.etree.ElementTree as ET
import requests
from lxml import etree as ET
from tqdm import tqdm

from config import *
from download_page import convert_url_to_local_path, strip_query_from_url
from main import login
from make_driver import driver

# toc_path = BASE_PATH / 't3Portal/external/en/rm/RM30G0U/toc.xml'
# # toc_url = f'{BASE_URL}/t3Portal/external/en/rm/RM30G0U/toc.xml'
#
# from bs4 import BeautifulSoup
# toc = open(toc_path, 'r').read().replace('\xa0', '')
# soup = BeautifulSoup(toc, features='xml')
# tocdata = soup.find_all('tocdata')
# for tag in tocdata:
#     tag.decompose()
# soup.find('termdata').decompose()
# soup.find('xmltoc').attrs = None
#
# with open('manual/toc.xml', 'w') as f:
#     xml_out = str(soup.prettify())
#     # xml_out = re.sub(r'\s+', '', xml_out)
#     f.write(xml_out)


tree = ET.parse('manual/toc.xml')
root = tree.getroot()
items = root.findall(".//item[@href]")
items = [item for item in items if item.attrib.get('href')]
page_map = {}
a = []
for item in items:
    href = item.attrib.get('href')
    if not href:
        continue
    page_title = item.find('name').text.strip()
    # file_name = page_title.split('; ')[0]
    # years = page_title.split('; ')[-1]
    # a.append(page_title.split(';')[-1])
    # page_title = page_title.split(';')
    # file_name = page_title[0]
    # parent_dir = page_title
    # print(href)
    path = [x.find('name').text.strip() for x in item.iterancestors('item')][::-1]
    path.append(page_title)
    path = [x.replace('/', '-') for x in path]
    print('/'.join(path))
    page_map[href] = path

login()

pages = list(page_map.keys())
for page in tqdm(pages):
    url = f'{BASE_URL}{page}'
    save_to = BASE_PATH / page.lstrip('/')
    save_to.parent.mkdir(parents=True, exist_ok=True)
    driver.get(url)
    page_source = driver.page_source
    with open(save_to, 'w') as f:
        f.write(page_source)

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
