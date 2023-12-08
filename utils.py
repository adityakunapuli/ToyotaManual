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
    with open(BASE_PATH / 'toc.xml', 'wb') as f:
        f.write(xml.content)
    print(f"Saved TOC XML to: {BASE_PATH / 'toc.xml'}")
    return xml.content


def get_toc_json(xml=None):
    if not xml:
        xml = get_toc_xml()
    tree = ET.fromstring(xml)
    root = tree.getroottree()
    items = root.findall('.//item[@href]')
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
        f.write(json.dumps(page_map, indent=4))
    print(f"Saved TOC JSON to: {BASE_PATH / 'toc.json'}")
    return page_map


def dict_to_nested_dict_with_links(input_dict):
    nested_dict = {}

    for url, inner_list in input_dict.items():
        current_dict = nested_dict

        for item in inner_list[:-2]:
            current_dict = current_dict.setdefault(item, {})

        key = inner_list[-2]
        value = f'<a href="{url}" target="page_frame">{inner_list[-1]}</a>'

        if key not in current_dict:
            current_dict[key] = value
        else:
            if not isinstance(current_dict[key], list):
                current_dict[key] = [current_dict[key]]
            current_dict[key].append(value)

    return nested_dict
