from pathlib import Path

from .credentials import INFO

ICON_PLUS = 'icons/plus.gif'
ICON_MINUS = 'icons/minus.gif'
ICON_PAGE = 'icons/page.gif'
ICON_FOLDERCLOSED = 'icons/folder.gif'
ICON_FOLDEROPEN = 'icons/folderopen.gif'
ROOT_FOLDER = 'LEXUS 2014-2024 IS200T IS250 IS300 IS350 IS500 Repair Manual (RM30G0U)'
BASE_PATH = Path('saved')
BASE_URL = 'https://techinfo.toyota.com'
END_PATH = Path('saved/t3Portal/document/rm/RM30G0U/xhtml')

VEHICLE_CODES = {
    'IS250': 'RM30G0U',
    'RAV4' : 'RM01M0U'
}

TECHNICIAN_MANUAL_URL = 'https://techinfo.toyota.com/t3Portal/resources/jsp/siviewer/index.jsp?dir=rm/RM30G0U'
CATEGORIES = ['General', 'Audio - Video- Visual - Telematics', 'Brake', 'Drivetrain', 'Engine - Hybrid System', 'Power Source - Network', 'Steering', 'Suspension',
              'Vehicle Exterior', 'Vehicle Interior']

AUTHENTICATION_URL = 'https://ep.fram.idm.toyota.com/openam/json/realms/root/realms/dealerdaily/authenticate?authIndexType=service&authIndexValue=Techinfo'

AUTHENTICATION_HEADERS = {
    'user-agent'        : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
    'x-openam-username' : INFO['username'],
    'x-openam-password' : INFO['password'],
    'content-type'      : 'application/json',
    'content-length'    : '0',
    'accept'            : '*/*',
    'accept-language'   : 'en-US,en;q=0.5',
    'accept-encoding'   : 'gzip, deflate, br',
    'accept-api-version': 'resource=2.0, protocol=1.0',
    'x-requested-with'  : 'X-FR-TMNA-Rest-API',
    'sec-fetch-dest'    : 'empty',
    'sec-fetch-mode'    : 'cors',
    'sec-fetch-site'    : 'same-site',
    'te'                : 'trailers'
}

ENGINE_CODES = [
    '2GR-FSE',
    'CRUISE',
    '8AR-FTS',
    '2GR-FKS',
    '2UR-GSE',
    '4GR-FSE',
]

UPPER_CASE = ENGINE_CODES + [
    'ECU',
    'SAE',
    'SST',
    'SSM'
    'IS200T',
    'AA81E',
    'AXLE',
    'UF1AE',
    'AA80E',
    'A960E',
    'DRIVE',
    'A760H',
    'TC',
    'CG',
    'SFI',
    'ECM',
]
