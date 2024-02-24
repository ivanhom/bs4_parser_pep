from pathlib import Path


class HTMLTag():
    A = 'a'
    DIV = 'div'
    DL = 'dl'
    H1 = 'h1'
    LI = 'li'
    SECTION = 'section'
    TABLE = 'table'
    TBODY = 'tbody'
    TD = 'td'
    TR = 'tr'
    UL = 'ul'


class OutputType():
    PRETTY = 'pretty'
    FILE = 'file'


ENCODING_STANDART = 'utf-8'
PARSER_TYPE = 'lxml'

BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'

LATEST_VERSION_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
PDF_A4_PATTERN = r'.+pdf-a4\.zip$'

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
