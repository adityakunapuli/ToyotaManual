import json

import requests
from lxml import etree as ET

from config import *


def get_authenticated_session():
    session = requests.Session()
    session.post(AUTHENTICATION_URL, headers=AUTHENTICATION_HEADERS)
    return session


def get_toc_xml():
    session = get_authenticated_session()
    toc_url = f'{BASE_URL}/t3Portal/external/en/rm/RM30G0U/toc.xml'
    xml = session.get(toc_url, verify=False)
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
    with open(BASE_PATH / 'toc.json', 'w') as f:
        f.write(json.dumps(page_map, indent=5))
    return page_map

