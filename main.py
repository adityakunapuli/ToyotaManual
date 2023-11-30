import json
import re
# noinspection PyUnresolvedReferences
import time

from config import *
from config.credentials import INFO
from download_page import download_pages
from generate_nav_tree import generate_nav_graph
from make_driver import driver
from utils import click_link, countdown_timer, reheat_navigation_soup, reheat_soup, wait_until


def login():
    driver.get(BASE_URL)
    # enter password
    driver.find_element(by='id', value='username').send_keys(INFO['username'])
    driver.find_element(by='id', value='password').send_keys(INFO['password'])
    driver.find_element(by='id', value='externalloginsubmit').click()
    # driver.maximize_window()
    wait_until(value='/html/body/div[4]/div[3]/div/div[1]/table/tbody/tr/td[6]/a')
    driver.get(TECHNICIAN_MANUAL_URL)


def open_subfolders(div_id, pluses=None):
    if pluses is None:
        div = reheat_soup().find(attrs={'id': div_id})
        pluses = div.find_all(attrs=dict(src=ICON_FOLDERCLOSED))
    for plus in pluses:
        clickable_element_id = plus.parent.get('id')
        click_link(clickable_element_id)
    div = reheat_soup().find(attrs={'id': div_id})
    pluses = div.find_all(attrs=dict(src=ICON_FOLDERCLOSED))
    if len(pluses) > 0:
        return open_subfolders(div_id, pluses)


def open_folder(clickable_element_id):
    click_link(elem_id=clickable_element_id)
    countdown_timer(3, silent=True)
    folder = reheat_soup()(attrs=dict(src=ICON_FOLDEROPEN))[0]
    parent_table = folder.find_parent('table')
    div = parent_table.find_next_sibling('div')
    open_subfolders(div_id=div.get('id'))


def list_parent_folders():
    parent_folders = {}
    for img in reheat_navigation_soup()(attrs=dict(src=ICON_PLUS)):
        if img.get('name'):
            continue
        # find parent `td` element
        parent_td = img.find_parent('td')
        # find first `a` element with non-empty `id` tag
        a = parent_td.find('a', attrs={'id': re.compile('.*')})
        parent_folders[parent_td.text] = {
            'a' : a.get('id'),
            'td': parent_td.get('id')
        }
    return parent_folders


def reset_nav_tree():
    driver.get(TECHNICIAN_MANUAL_URL)
    driver.switch_to.default_content()
    driver.switch_to.frame('navigation_frame')


if __name__ == '__main__':
    login()

    # reset_nav_tree()
    parent_folders = list_parent_folders()

    failed_path = BASE_PATH / 'failed.json'
    if failed_path.exists():
        with open(failed_path, 'r') as f:
            failed = json.load(f)
    else:
        failed = {}

    nav_tree_path = BASE_PATH / 'navigation_tree.json'
    if nav_tree_path.exists():
        with open(nav_tree_path, 'w') as f:
            tree = json.load(f)
    else:
        tree = {}

    for i, (category, element_ids) in enumerate(parent_folders.items(), 1):
        if category not in ['Suspension', 'Vehicle Exterior', 'Vehicle Interior']:
            continue
        print(f'Starting...{category} ({i}/{len(parent_folders)})')
        # expand the parent folder
        clickable_element_id = element_ids['a']
        open_folder(clickable_element_id)
        sub_tree = generate_nav_graph()
        tree.update(sub_tree)
        failed[category] = download_pages(category=category)
        # print(f'\tCompleted')
        # countdown_timer(10)
        reset_nav_tree()
        countdown_timer(3, silent=True)

    # failed = {k: [x.get('id') for x in v] for k, v in failed.items()}
    with open(BASE_PATH / 'failed.json', 'w') as f:
        f.write(json.dumps(failed))

    with open(BASE_PATH / 'navigation_tree.json', 'w') as f:
        f.write(json.dumps(tree))
