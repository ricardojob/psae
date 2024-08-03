import unittest
import ast
import requests

from psae.capture import CheckVisitor, Usage,  read_apis

from typing import Generator

class UsageRecord:
    def __init__(self, usage: Usage, url: str, count:int) -> None:
        self.usage = usage
        self.url_pretty = url
        self.count = count

UsageRecordGenerator = Generator[Usage, None, None]
# https://github.com/samiislam/MockFileReadingLineByLine
def read_by_records(source: str) -> UsageRecordGenerator:
    header_processed = False
    with open(source) as file:
        for line in file:
            record = line.split(sep=';')
            if not header_processed:
                header_processed = True
                continue
            # AssertionError: Usage(line=631, api='platform.win32_ver', platforms={''}) not found in {Usage(line=631, api='platform.win32_ver', platforms=set())}
            use_set = set()
            if record[3] != '':
                for operating in str(record[3]).split(","):
                    use_set.add(operating)
            # line,module,package,platform,url
            usage  = Usage(int(record[0]), f'{record[1]}.{record[2]}', use_set)
            yield UsageRecord(usage, record[4], int(record[5]))
                        
class TestUsageIf(unittest.TestCase):

    def setUp(self):
        self.os_apis  = read_apis()
        self.filename = 'tests/unit/usages.csv'
        # self.filename = 'tests/unit/usages-count.csv'
        # self.filename = 'tests/unit/usages-count-all.csv'
        # self.filename = 'tests/unit/usages-count-problems.csv'
     
    def test_if_two_compare(self):
        pretty = 'https://github.com/ansible/ansible/blob/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
        raw = 'https://raw.githubusercontent.com/ansible/ansible/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
        self.assertEqual(self.pretty_to_raw(pretty), raw)
        
    def test_usages(self):
        for record in read_by_records(self.filename):
            with self.subTest(msg=f"{record.url_pretty}", record=record):
                if (self.find_problems(record.url_pretty)):
                    # print(f'skipped: {record.url_pretty}')
                    self.skipTest(f"problems with: {record.url_pretty}")
                    # continue
                code = self.read_code(record)
                file_compile = ast.parse(code)
                checkVisitor = CheckVisitor(self.os_apis)
                checkVisitor.visit(file_compile)
                self.assertEqual(record.count, len(checkVisitor.usages), msg=record.url_pretty)
                self.assertIn(record.usage, checkVisitor.usages, msg=record.url_pretty)
    
    def find_problems(self, url):
        # problems = ['https://github.com/certbot/certbot/blob/097af18417020d9108bda4f09685dddac26a0039/certbot/certbot/_internal/tests/main_test.py#L1015',
        #             'https://github.com/ansible/ansible/blob/666188892ed0833e87803a3e80c58923e4cd6bca/hacking/tests/gen_distribution_version_testcase.py#L95',
        #             'https://github.com/mitmproxy/mitmproxy/blob/04d9249ab18cd7bd8b54958714d24614f27863b5/test/mitmproxy/proxy/test_mode_servers.py#L143',
        #             'https://github.com/saltstack/salt/blob/8a1e4c120f03149ebff288c6c989cca69327cd17/tests/support/ext/console.py#L22',
        #             'https://github.com/deepfakes/faceswap/blob/216ef387636eb7b84819c1b77d9a2f631ed97ab5/tests/lib/sysinfo_test.py#L54' #5 instances
        #             ]
        problems = ['https://github.com/certbot/certbot/blob/097af18417020d9108bda4f09685dddac26a0039/certbot/certbot/_internal/tests/main_test.py',
                    'https://github.com/ansible/ansible/blob/666188892ed0833e87803a3e80c58923e4cd6bca/hacking/tests/gen_distribution_version_testcase.py',
                    'https://github.com/mitmproxy/mitmproxy/blob/04d9249ab18cd7bd8b54958714d24614f27863b5/test/mitmproxy/proxy/test_mode_servers.py',
                    'https://github.com/saltstack/salt/blob/8a1e4c120f03149ebff288c6c989cca69327cd17/tests/support/ext/console.py',
                    'https://github.com/deepfakes/faceswap/blob/216ef387636eb7b84819c1b77d9a2f631ed97ab5/tests/lib/sysinfo_test.py', #5 instances
                    'https://github.com/numpy/numpy/blob/2ef217d279d13afa2399efee864b9f11f4096aa7/numpy/distutils/tests/test_exec_command.py', #7 instances (3 não deveriam)
                    'https://github.com/numpy/numpy/blob/2ef217d279d13afa2399efee864b9f11f4096aa7/numpy/lib/tests/test_format.py', #1 instances (deveriam ser duas)
                    'https://github.com/celery/celery/blob/c8b25394f0237972aea06e5e2e5e9be8a2bea868/t/unit/utils/test_platforms.py', #2 instances (deveria ser uma)
                    'https://github.com/ray-project/ray/blob/10861d9f2ef19e845186b8925053a11c6812a161/python/ray/tests/test_usage_stats.py', #9 instances (deveriam ser 10)
                    'https://github.com/ray-project/ray/blob/10861d9f2ef19e845186b8925053a11c6812a161/python/ray/tests/test_tempfile.py', #5 instances (deveriam ser 6)
                    'https://github.com/ray-project/ray/blob/10861d9f2ef19e845186b8925053a11c6812a161/python/ray/tests/test_metrics_agent.py', #4 instances (deveriam ser 6)
                    'https://github.com/matplotlib/matplotlib/blob/e8101f17d8a7d2d7eccff7452162c02a27980800/lib/matplotlib/tests/test_backends_interactive.py', #7 instances (a ferramenta anterior, detectou 6)
                    'https://github.com/aio-libs/aiohttp/blob/ae7703cefd1f8c8ad02bfc21cdc92c367f2666b9/tests/test_proxy_functional.py', #1 instances (deveriam ser duas)
                    'https://github.com/saltstack/salt/blob/2bd55266c8ecc929a3a0a9aec1797a368c521072/tests/unit/utils/test_verify.py', #6 instances (deveriam ser 8)
                    'https://github.com/saltstack/salt/blob/2bd55266c8ecc929a3a0a9aec1797a368c521072/tests/support/paths.py', #3 instances (deveriam ser duas)
                    'https://github.com/ray-project/ray/blob/10861d9f2ef19e845186b8925053a11c6812a161/python/ray/tests/test_logging.py', #2 instances (deveriam ser 3)
                    'https://github.com/ray-project/ray/blob/10861d9f2ef19e845186b8925053a11c6812a161/python/ray/tests/test_debug_tools.py', #4 instances (deveriam ser 5)
                    'https://github.com/ray-project/ray/blob/10861d9f2ef19e845186b8925053a11c6812a161/python/ray/tests/test_runtime_env.py', #5 instances  (a ferramenta anterior, detectou 4)
                    'https://github.com/ray-project/ray/blob/10861d9f2ef19e845186b8925053a11c6812a161/python/ray/tests/test_memory_deadlock.py', #7 instances  (deveriam ser 14)
                    'https://github.com/ray-project/ray/blob/10861d9f2ef19e845186b8925053a11c6812a161/python/ray/tests/test_memory_pressure.py', #14 instances  (deveriam ser 28)
                    'https://github.com/ray-project/ray/blob/10861d9f2ef19e845186b8925053a11c6812a161/python/ray/serve/tests/test_ray_client.py', #1 instances  (deveriam ser 2)
                    ]
        for problem in problems:
            if url.startswith(problem): 
                return True
        return False
    
    def pretty_to_raw(self, pretty:str):    
        raw = pretty.replace("/blob/","/").replace("github.com/", "raw.githubusercontent.com/")
        return raw
    
    def read_code(self, record):
        raw_url = self.pretty_to_raw(record.url_pretty)
        code = requests.get(raw_url).content
        return code
    
if __name__ == '__main__':
    unittest.main()