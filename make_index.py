import json
import re

from bs4 import BeautifulSoup

from config import *
from utils import dict_to_nested_dict_with_links


def long_substr(data):
    substrs = lambda x: {x[i:i + j] for i in range(len(x)) for j in range(len(x) - i + 1)}
    s = substrs(data[0])
    for val in data[1:]:
        s.intersection_update(substrs(val))
    return max(s, key=len)


def format_title(text):
    if ';' not in text:
        return title_case(text)
    length = len(text)
    break_at = length - text[::-1].find(';')
    title = text[:break_at - 1]
    title = title.replace(';', ':')

    desc = re.sub('\xa0+', ' ', text[break_at:].strip())
    models, years = re.findall(r'.*? MY (.*) \[(.*)\]', desc)[0]
    models = models.split(' ')
    common = long_substr(models)
    models = common + '/'.join([x.replace(common, '') for x in models])
    title = title_case(title)
    page_title = f'{title} [{years}] [{models}]'
    return page_title


def title_case(x):
    x_split = x.split(' ')
    s = []
    for w in x_split:
        s.append(w.upper() if w.upper() in UPPER_CASE else w.title())
    return ' '.join(s)


def dict_to_html(o, nested=False):
    s = ""
    if isinstance(o, dict):
        s += f'<ul class="{"nested" if nested else "treeview-animated-list"}">\n'
        for k, v in o.items():
            s += f'''<li class="treeview-animated-items">
                            <a class="closed"> <i class="fas fa-angle-right"></i>
                                <span><i class="far fa-folder-open ic-w mx-1"></i>
                                    {k}</span></a>''' + dict_to_html(v, True) + '''
                                
                            </li>'''
        s += '</ul>'
    elif isinstance(o, list):
        s += '<ul class="nested">\n'
        if not o:
            return str(o)
        else:
            for v in o:
                s += f'''<li>
                     <div class="treeview-animated-element">
                        <i class="fas fa-file ic-w mr-1"></i>
                            {v}
                        </div>
                    </li>'''
            s += "</ul>"
    else:
        return f'''
        <ul class="nested">
            <li>
                <div class="treeview-animated-element">
                <i class="fas fa-file ic-w mr-1"></i>
                    {str(o)}
                </div>
            </li>
        </ul>
        '''
    return re.sub('\s+', ' ', s)


def convert_toc_xml_to_menu():
    with open(BASE_PATH / 'toc.json', 'r') as f:
        toc = json.load(f)

    new_toc = {}
    for k, v in toc.items():
        new_v = []
        for w in v:
            engine_code = [x for x in w.split(' ') if x in ENGINE_CODES]
            if engine_code:
                engine_code = engine_code[0]
                sub_dir = w.replace('(', '').replace(')', '').replace(engine_code, '').strip()
                new_v.append(format_title(sub_dir))
                new_v.append(engine_code)
            else:
                new_v.append(format_title(w))
        new_toc[k] = new_v

    d = dict_to_nested_dict_with_links(new_toc)

    html_string = dict_to_html(d)
    soup = BeautifulSoup(html_string, features='html.parser')
    return soup.prettify()


if __name__ == '__main__':
    html = convert_toc_xml_to_menu()
    html = html.replace('t3Portal/', 'ToyotaTechInfoRipper/saved/t3Portal/')
    with open('template/template.html', 'r') as template:
        template = template.read().replace('% VAR %', html)
    with open('saved/index.html', 'w') as index:
        index.write(template)
