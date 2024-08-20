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

class TestUsageIf():
    pass

def test_generator(record, usages):
    def test(self):
        self.assertEqual(record.count, len(usages), msg=record.url_pretty)
        self.assertIn(record.usage, usages, msg=record.url_pretty)
    return test

def find_problems_generator(url):
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

def read_code_generator(record):
        raw_url = pretty_to_raw_generator(record.url_pretty)
        code = requests.get(raw_url).content
        return code    
    
def pretty_to_raw_generator(pretty:str):    
        raw = pretty.replace("/blob/","/").replace("github.com/", "raw.githubusercontent.com/")
        return raw
    
if __name__ == '__main__':
    for record in read_by_records('tests/unit/usages-count-all.csv'):
        if (find_problems_generator(record.url_pretty)):
            print(f'skipped: {record.url_pretty}')
            continue
        code = read_code_generator(record)
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(read_apis())
        checkVisitor.visit(file_compile)
        test_name = 'test_%s' % record.url_pretty
        test = test_generator(record, checkVisitor.usages)
        setattr(TestUsageIf, test_name, test)
    unittest.main()

# from unittest import TestCase

# class TestDemonstrateSubtest(TestCase):
#     def test_works_as_expected(self):
#         for record in read_by_records('tests/unit/usages.csv'):
#             with self.subTest(record):
#                 if (find_problems_generator(record.url_pretty)):
#                     print(f'skipped: {record.url_pretty}')
#                     continue
#                 code = read_code_generator(record)
#                 file_compile = ast.parse(code)
#                 checkVisitor = CheckVisitor(read_apis())
#                 checkVisitor.visit(file_compile)
#                 self.assertEqual(record.count, len(checkVisitor.usages), msg=record.url_pretty)
#                 self.assertIn(record.usage, checkVisitor.usages, msg=record.url_pretty)
# if __name__ == '__main__':
#     unittest.main()