import os
import json

import re
from pathlib import Path, PosixPath
from typing import Dict

from tqdm import tqdm


def map_all_docs() -> Dict[str, PosixPath]:
    d = {}
    files = Path('saved').glob('**/*.html')
    for file in files:
        if file.is_file() and file.name.endswith('html'):
            doc_id = re.findall(r'\((RM\w+)\)', str(file))[0]
            d[doc_id] = file
    return d


def find_doc_links(path):
    with open(path, 'r') as f:
        html = f.read()
    links = re.findall(r'href="(.*xhtml/RM.*?\.html.*)"', html)
    if not links:
        return
    link_map = {}
    for link in links:
        doc_id = re.findall('xhtml/(RM.*?)\.html', link)[0]
        link_map[doc_id] = link
    return link_map


def fix_links_in_page(path):
    links = find_doc_links(path)
    if not links:
        return

    with open(path, 'r') as f:
        html = f.read()

    source_file_dir = str(path.parent)

    failed = []
    for link_doc_id, old_url in links.items():
        try:
            target_file_path = d[link_doc_id]
            common_root = os.path.commonpath([path, target_file_path])
            target_file_dir = str(target_file_path) \
                .replace(common_root, '') \
                .lstrip('/')
            # number of levels up to `cd`
            up_levels = source_file_dir \
                .replace(common_root, '') \
                .count('/')
            new_url = f'{"../" * up_levels}{target_file_dir}'
            html = html.replace(old_url, new_url)
        except:
            failed.append(link_doc_id)

    with open(path, 'w') as f:
        f.write(html)

    return failed


def fix_all_links():
    files = list(Path('saved').glob('**/*.html'))
    failed = {}
    stats = {'files_scanned': 0, 'files_needing_fix': 0}
    for file in tqdm(files):
        if file.is_file() and file.name.endswith('html'):
            stats['files_scanned'] += 1
            fails = fix_links_in_page(file)
            if fails:
                failed[file] = fails
                stats['files_needing_fix'] += 1

    failed_doc_ids = set()
    for k, v in failed.items():
        failed_doc_ids.update(set(v))

    stats['doc_ids'] = len(failed_doc_ids)
    print(json.dumps(stats, indent=4))
    return failed_doc_ids

# if __name__ == '__main__':
#     d = map_all_docs()
#     files = list(Path('saved').glob('**/*.html'))
#     failed = {}
#     for file in tqdm(files):
#         if file.is_file() and file.name.endswith('html'):
#             fails = fix_links_in_page(file)
#             if fails:
#                 failed[file] = fails
#
#     failed_doc_ids = set()
#     for k, v in failed.items():
#         failed_doc_ids.update(set(v))
