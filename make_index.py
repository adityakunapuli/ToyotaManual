import json
import re
from collections import defaultdict
from copy import deepcopy

from bs4 import BeautifulSoup

from config import *


def long_substr(data):
    substrs = lambda x: {x[i:i + j] for i in range(len(x)) for j in range(len(x) - i + 1)}
    s = substrs(data[0])
    for val in data[1:]:
        s.intersection_update(substrs(val))
    return max(s, key=len)


def format_title(last, page_path):
    length = len(last)
    break_at = length - last[::-1].find(';')
    title = last[:break_at - 1]
    title = title.replace(';', ':')

    desc = re.sub('\xa0+', ' ', last[break_at:].strip())
    models, years = re.findall(r'.*? MY (.*) \[(.*)\]', desc)[0]
    models = models.split(' ')
    common = long_substr(models)
    models = common + '/'.join([x.replace(common, '') for x in models])
    page_path = page_path.strip('/')

    title = title_case(title)
    page_title = f'{title} [{years}] [{models}]'
    # UPPER_CASE
    html = f'<a href="{page_path}" target="main_content">{page_title}</a>'
    return html


def title_case(x):
    x_split = x.split(' ')
    # x = [w.title() for w in x_split if w not in UPPER_CASE]
    s = []
    for w in x_split:
        s.append(w if w in UPPER_CASE else w.title())
    return ' '.join(s)


# def parse_dict_to_html(d):
#     s = '<ul>'
#     for k, v in d.items():
#         s += f'<li>{k}\n'
#         if isinstance(v, dict):
#             s += parse_dict_to_html(v)


def printItems(dictObj, parent, indent):
    if len(dictObj):
        print('{}<ul>'.format('  ' * indent))
        for k, v in dictObj.iteritems():
            print('{}<li><input type="checkbox" id="{}-{}">{}</li>'.format(
                '  ' * (indent + 1), k, parent, k))
            printItems(v, k, indent + 1)
        print('{}</ul>'.format('  ' * indent))


def printitems(dictObj, indent=0):
    p = []
    p.append('<ul>\n')
    for k, v in dictObj.items():
        if isinstance(v, dict):
            p.append('<li>' + k + ':')
            p.append(printitems(v))
            p.append('</li>')
        else:
            p.append('<li>' + k + ':' + v + '</li>')
    p.append('</ul>\n')
    return '\n'.join(p)


def get_html(o):
    s = ""
    if isinstance(o, dict):
        s += '<ul id="navigation_tree">\n'
        for k, v in o.items():
            s += f'<li>{k}' + get_html(v) + "</li>\n"
        s += '</ul>'
    elif isinstance(o, list):
        s += "<ul>\n"
        if not o:
            return str(o)
        else:
            out = []
            for v in o:
                ss = ""
                for kk, vv in v.items():
                    ss += f"<li><b>{kk}</b>:" + get_html(vv) + " </li>\n"
                out.append(ss)
            s += "<br>\n".join(out)
            s += "</ul>"
    else:
        return f'<br>{str(o)}'
    return s


def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


if __name__ == '__main__':
    with open(BASE_PATH / 'toc.json', 'r') as f:
        toc = json.load(f)

    new_toc = {}
    for k, v in toc.items():
        # if 'RM100000000N4P5' in k:
        #     print(k)
        #     break

        new_v = []
        for w in v:
            engine_code = [x for x in w.split(' ') if x in ENGINE_CODES]
            if engine_code:
                engine_code = engine_code[0]
                new_v.append(engine_code)
                sub_dir = w.replace('(', '').replace(')', '').replace(engine_code, '').strip()
                new_v.append(sub_dir)
            else:
                new_v.append(w)

        new_toc[k] = new_v

    d = defaultdict(dict)

    for page_path, v in deepcopy(new_toc).items():
        v = [x.replace('\xa0', '') for x in v]
        last = v.pop(-1)
        last = format_title(last, page_path)
        keys = [title_case(key) for key in v]
        nested_set(d, keys, last)

    # print(json.dumps(dict(d), indent=4))

    # d = d['General']['Introduction']
    html_string = get_html(d)
    soup = BeautifulSoup(html_string, features='html.parser')
    #
    # tag_a = soup.new_tag('a', attrs={'class': 'closed'})
    # tag_i = soup.new_tag('i', attrs={'class': 'fas fa-angle-right'})
    # tag_span = soup.new_tag('span')
    # tag_i2 = soup.new_tag('i', attrs={'class': 'far fa-envelope-open ic-w mx-1'})
    # tag_div = soup.new_tag('div', attrs={'class': 'treeview-animated-element'})
    #
    # # li.insert(0)
    #
    # for i, ul in enumerate(soup.find_all('ul', recursive=True)):
    #     if i == 0:
    #         ul.attrs = {'class': 'mb-1 pl-3 pb-2'}
    #     else:
    #         ul.attrs = {'class': 'nested'}
    # for li in soup.find_all('li', recursive=True):
    #     if li.text == 'General':
    #         print(li)
    #     li.attrs = {'class': 'treeview-animated-items'}

    # soup.find('ul').attrs = {'id': 'navigation_tree', 'class': 'jslists'}
    template = open('saved/index.html', 'r').read().replace('% VAR %', soup.prettify())
    with open('saved/index2.html', 'w') as f:
        f.write(template)
