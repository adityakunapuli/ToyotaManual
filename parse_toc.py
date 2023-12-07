# import xml.etree.ElementTree as ET
from collections import defaultdict

from bs4 import BeautifulSoup
from lxml import etree as ET

from config import BASE_PATH


def xml_to_dict_with_links(element):
    result = {}
    if element.tag == 'xmltoc':
        for child in element:
            result[child.text] = xml_to_dict_with_links(child)
    elif element.tag == 'item':
        result = {}
        for child in element:
            if child.tag == 'item':
                result[child.find('name').text] = xml_to_dict_with_links(child)
            elif child.tag == 'name':
                result[child.text] = xml_to_dict_with_links(child)
            elif child.tag == 'item':
                result[child.find('name').text] = xml_to_dict_with_links(child)
    elif element.tag == 'name':
        result = element.text
    elif element.tag == 'item' and element.attrib.get('href'):
        result = f"<a href='{element.attrib['href']}'>{element.find('name').text}</a>"
    return result


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    root = minimize_xml(root)
    return xml_to_dict_with_links(root)


def minimize_xml(root):
    for tag in root.findall('.//tocdata'):
        for child in tag.getchildren():
            tag.remove(child)
        tag.getparent().remove(tag)
    termdata = root.find('termdata')
    for child in termdata.getchildren():
        termdata.remove(child)
    termdata.getparent().remove(termdata)
    with open(BASE_PATH / 'toc_min.xml', 'wb') as f:
        f.write(ET.tostring(root))
    return root


file_path = BASE_PATH / 'toc.xml'

d = {
    'LEXUS 2014-2024 IS200T IS250 IS300 IS350 IS500 Repair Manual (RM30G0U)':
        {
            'General': {
                'Introduction': {
                    'HOW TO USE THIS MANUAL': '<a href=""/t3Portal/document/rm/RM30G0U/xhtml/RM1000000006BKQ.html"">GENERAL INFORMATION</a>'
                }
            }
        }
}

d = parse_xml_file(file_path)
with open('/Users/maradmin/Library/Application Support/JetBrains/PyCharm2020.3/scratches/asd.json', 'w') as f:
    f.write(json.dumps(d, indent=4))


def parse(root):
    k = root.find('name')
    d = defaultdict(list)
    d[k.text] = []


def xml_to_html_list(element):
    html = "<ul>"
    for child in element:
        html += "<li>"

        if child.text:
            html += child.text

        if child.attrib.get('href'):
            html += f'<a href="{child.attrib["href"]}">'

        if child:
            html += xml_to_html_list(child)

        if child.attrib.get('href'):
            html += '</a>'

        html += "</li>"
    html += "</ul>"
    return html


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return xml_to_html_list(root)


# Example usage:
nested_dict = parse_xml_file('/Users/maradmin/Library/Application Support/JetBrains/PyCharm2020.3/scratches/scratch.xml')
print(nested_dict)


def xml_to_html_list(element):
    html = "<ul>"
    for child in element:
        html += "<li>"
        if child.text:
            html += child.text
        if child:
            html += xml_to_html_list(child)
        html += "</li>"
    html += "</ul>"
    return html


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return xml_to_html_list(root)


# Example usage:
file_path = '/Users/maradmin/Library/Application Support/JetBrains/PyCharm2020.3/scratches/scratch.xml'
html_list = parse_xml_file(file_path)
print(html_list)

print(BeautifulSoup(html_list, features='lxml').prettify())

import xml.etree.ElementTree as ET


def xml_to_html_menu(element):
    html = "<ul class='sidenav-list'>"
    for child in element:
        html += "<li class='sidenav-item'>"

        if child.text:
            html += f"<a href='#'>{child.text}</a>"

        if child.attrib.get('href'):
            html += f"<a href='{child.attrib['href']}' class='sidenav-link'>{child.text}</a>"

        if child:
            html += xml_to_html_menu(child)

        html += "</li>"
    html += "</ul>"
    return html


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return xml_to_html_menu(root)


# Example usage:
file_path = '/Users/maradmin/Library/Application Support/JetBrains/PyCharm2020.3/scratches/scratch.xml'
html_menu = parse_xml_file(file_path)

# Wrap the generated HTML in the necessary structure from the MDBootstrap example
final_html = f'''
<!doctype html>
<html lang="en">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet"/>
        <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" rel="stylesheet"/>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.1.0/mdb.min.css" rel="stylesheet"/>
        <style>
            html {{
                font-size: 10px;
            }}
            
            i {{margin: 0 0.6em;}}
            
            ol, ul {{
                list-style-type: none;
                padding-left: 0 !important;
            }}
            
            a:link {{
                text-decoration: none !important;
            }}
            
            .treeview-animated-list {{
                padding-left: 0 !important;
            }}
        </style>
    </head>
    
<body>
  <div id="sidenav" class="sidenav">
    {html_menu}
  </div>
   
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.4/umd/popper.min.js"></script>
    <script type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.5.0/js/bootstrap.min.js"></script>
    <script type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.19.1/js/mdb.min.js"></script>
    
    <script>
        // Treeview Initialization
        $(document).ready(function () {{
            $('.treeview-animated').mdbTreeview();
        }});
    </script>

</body>
</html>
'''

print(final_html)

with open('/Users/maradmin/PycharmProjects/ToyotaTechInfoRipper/repair_manual/test.html', 'w') as f:
    f.write(final_html)


def xml_to_bootstrap_sidenav(element):
    html = "<ul class='navbar-nav'>"
    for child in element:
        html += "<li class='nav-item'>"

        if child.text:
            html += f"<a class='nav-link' href='#'>{child.text}</a>"

        if child.attrib.get('href'):
            html += f"<a class='nav-link' href='{child.attrib['href']}'>{child.text}</a>"

        if child:
            html += xml_to_bootstrap_sidenav(child)

        html += "</li>"
    html += "</ul>"
    return html


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return xml_to_bootstrap_sidenav(root)


# Example usage:
html_sidenav = parse_xml_file(file_path)

# Wrap the generated HTML in the necessary structure from Bootstrap 5
final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Add your head content here -->
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        {html_sidenav}
      </div>
    </div>
  </nav>
</body>
</html>
"""


def xml_to_collapsible_bootstrap_sidenav(element):
    html = "<ul class='navbar-nav'>"
    for child in element:
        html += "<li class='nav-item'>"

        if child.text:
            html += f"<a class='nav-link' href='#'>{child.text}</a>"

        if child.attrib.get('href'):
            html += f"<a class='nav-link' href='{child.attrib['href']}'>{child.text}</a>"

        if child:
            html += "<button class='navbar-toggler' type='button' data-bs-toggle='collapse' data-bs-target='#submenu'>"
            html += "<span class='navbar-toggler-icon'></span>"
            html += "</button>"
            html += "<div class='collapse' id='submenu'>"
            html += xml_to_collapsible_bootstrap_sidenav(child)
            html += "</div>"

        html += "</li>"
    html += "</ul>"
    return html


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return xml_to_collapsible_bootstrap_sidenav(root)


# Example usage:
html_sidenav = parse_xml_file(file_path)

# Wrap the generated HTML in the necessary structure for a collapsible Bootstrap 5 sidenav
final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        {html_sidenav}
      </div>
    </div>
  </nav>

  <!-- Bootstrap JS and Popper.js dependencies -->

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
</body>
</html>
"""

with open('/Users/maradmin/PycharmProjects/ToyotaTechInfoRipper/repair_manual/test.html', 'w') as f:
    f.write(final_html)
