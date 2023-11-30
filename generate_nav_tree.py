import json
import re
from collections import defaultdict

from config import *
from download_page import parse_title
from utils import reheat_navigation_soup


class Node:
    def __init__(self, indented_line):
        self.children = []
        self.level = len(indented_line) - len(indented_line.lstrip())
        self.text = indented_line.strip()

    def add_children(self, nodes):
        childlevel = nodes[0].level
        while nodes:
            node = nodes.pop(0)
            if node.level == childlevel:  # add node as a child
                self.children.append(node)
            elif node.level > childlevel:  # add nodes as grandchildren of the last child
                nodes.insert(0, node)
                self.children[-1].add_children(nodes)
            elif node.level <= self.level:  # this node is a sibling, no more children
                nodes.insert(0, node)
                return

    def as_dict(self):
        if len(self.children) > 1:
            return {self.text: [node.as_dict() for node in self.children]}
        elif len(self.children) == 1:
            return {self.text: self.children[0].as_dict()}
        else:
            return self.text


def find_icons(soup):
    icons = soup.find_all(attrs=dict(src=re.compile(r'icons/.*?.gif')))
    icons = [icon for icon in icons
             if icon.get('src') in [ICON_PLUS, ICON_MINUS, ICON_PAGE, ICON_FOLDERCLOSED]][1:]
    icons = [next(x.parents) for x in icons]
    icons = [next(x.parents) for x in icons]
    return icons


def generate_nav_graph():
    soup = reheat_navigation_soup()
    icons = find_icons(soup)

    lines = []
    # page_to_doc_id = {}
    for icon in icons:
        title = parse_title(icon.text, suffix=None)
        doc = icon.find_all('img', attrs={'name': re.compile('.*?')})
        doc_id = None
        if doc:
            doc = doc[0]
            a = doc.find_parent('a')
            doc_id = re.findall(r'xhtml/(RM.*?)\.html', a.get('href'))
            if doc_id:
                doc_id = doc_id[0]
                # page_to_doc_id[doc_id] = title
        # title = icon.text.replace('\xa0', '')

        parent_table = icon.find_parent('table')
        spaces = len(parent_table.find_all('img', attrs={'src': 'icons/empty.gif'}))
        if doc_id:
            line = f'{" " * spaces}{title}'
            lines.append(line)
            line_title_map = f'{" " * (spaces + 1)}{doc_id}'
            lines.append(line_title_map)
        else:
            line = f'{" " * spaces}{title}'
            lines.append(line)

        # if line not in lines:

    root = Node('root')
    root.add_children([Node(line) for line in lines if line.strip()])
    d = root.as_dict()['root']
    d = [x for x in d if isinstance(x, dict)][0]
    # print(json.dumps(d, indent=4))
    return d


def defaultify(d):
    if isinstance(d, dict):
        return defaultdict(lambda: None, {k: defaultify(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [defaultify(e) for e in d]
    else:
        return d
