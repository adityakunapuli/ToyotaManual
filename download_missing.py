import re
from pathlib import Path

from bs4 import BeautifulSoup
from tqdm import tqdm

from config import BASE_PATH
from download_page import download_page
from fix_links import fix_all_links
from main import login


def find_category(page_source):
    soup = BeautifulSoup(page_source)
    table = soup.find('table', attrs={'class': 'side'}).text.replace('\xa0', '')
    title = re.findall('Title: (.*)', table)[0]
    subdir = title.split(':')[0].replace('/', '-')
    return d[subdir]


def generate_category_map():
    category_map = {}
    folders = list(Path(BASE_PATH).glob('**'))
    for folder in folders:
        if len(folder.parents) != 3:
            continue
        folder_name = folder.name.upper()
        category_map[folder_name] = folder.parent.name
    return category_map


if __name__ == '__main__':
    failed_doc_ids = fix_all_links()
    d = generate_category_map()
    login()
    # reqs = driver.requests
    # for req in reqs:
    #     if req.url.startswith('https://techinfo.toyota.com/t3Portal/') and 'html' in req.url:
    #         break

    from make_driver import driver

    page_template = 'https://techinfo.toyota.com/t3Portal/document/rm/RM30G0U/xhtml/{doc_id}.html?sisuffix=ff&locale=en&siid=1701390950692'

    driver.switch_to.default_content()
    driver.switch_to.frame('manual_frame')

    failed_again = []
    # for doc_id in tqdm(failed_doc_ids):
    for doc_id in tqdm(failed_doc_ids):
        try:
            doc_url = page_template.format(doc_id=doc_id)
            driver.get(doc_url)
            page_source = driver.page_source
            category = find_category(page_source)
            download_page(category)
        except:
            failed_again.append(doc_id)

#             1315/2235
    print(failed_again)



"""
{
    "files_scanned": 5228,
    "files_needing_fix": 2402,
    "doc_ids": 3585
}
 79%|███████▊  | 2820/3585 [2:39:53<1:10:51,  5.56s/it]Timed out for saved/t3Portal/document/rm/RM30G0U/images/B346110N01.png
Timed out for saved/t3Portal/document/rm/RM30G0U/images/B346109N01.png
Timed out for saved/t3Portal/document/rm/RM30G0U/images/B346098N01.png
Timed out for saved/t3Portal/document/rm/RM30G0U/images/B346097N01.png
Timed out for saved/t3Portal/document/rm/RM30G0U/images/B346100.png
Timed out for saved/t3Portal/document/rm/RM30G0U/images/B346099.png
100%|██████████| 3585/3585 [4:01:26<00:00,  4.04s/it]
['RM10000000104YG', 'RM10000000104YH', 'RM1000000007TCJ', 'RM10000000072A7', 'RM1000000007TW9', 'RM100000000NDX6', 'RM1000000007S95', 'RM1000000011RNR', 'RM1000000007TCP', 'RM1000000006IH9', 'RM1000000007TZV', 'RM1000000006PHZ', 'RM1000000006HX7', 'RM1000000007OTN', 'RM1000000006J62', 'RM100000000727N', 'RM1000000006IGN', 'RM1000000007TCN', 'RM1000000006PIT', 'RM1000000006CXR', 'RM1000000006PI7', 'RM1000000006J61', 'RM1000000006IFP', 'RM100000000NDX7', 'RM1000000007BLN', 'RM1000000006XZK', 'RM1000000006JPM', 'RM1000000006JNP', 'RM1000000007SAI', 'RM10000000112Y4', 'RM10000000112XY', 'RM1000000006HX8', 'RM1000000006CXJ', 'RM1000000007BLR', 'RM1000000007TC5', 'RM1000000006JPP', 'RM1000000006PIR', 'RM1000000006I41', 'RM100000000727J', 'RM1000000006XZI', 'RM1000000006JPB', 'RM1000000007TB1', 'RM1000000007BLQ', 'RM1000000006I3W', 'RM1000000006J48', 'RM1000000006PI5', 'RM1000000006PIY', 'RM10000000071YP', 'RM1000000006JH8', 'RM1000000006JHA', 'RM1000000011QDD', 'RM1000000011S28', 'RM1000000006CXQ', 'RM10000000077JB', 'RM1000000006JPQ', 'RM1000000007OLQ', 'RM100000000NTQ1', 'RM1000000006CXK', 'RM1000000011QDF', 'RM1000000006IGJ', 'RM1000000006IGG', 'RM1000000006PI1', 'RM1000000006IGP', 'RM1000000007TZL', 'RM1000000006JND', 'RM100000000704X', 'RM100000000NVQH']
"""
