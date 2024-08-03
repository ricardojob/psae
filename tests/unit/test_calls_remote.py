import unittest
import ast
import requests

from psae.capture import CheckVisitor, Call,  read_apis

from typing import Generator

class CallRecord:
    # def __init__(self, call: Call, url: str, risk: int, handle: bool) -> None:
    def __init__(self, call: Call, url: str, risk: int, handle: str) -> None:
        self.call = call
        self.url_pretty = url
        self.risk = risk
        # self.handle = 'true' == handle.lower().capitalize()
        self.handle = handle

CallRecordGenerator = Generator[Call, None, None]
# https://github.com/samiislam/MockFileReadingLineByLine
def read_by_records(source: str) -> CallRecordGenerator:
    header_processed = False
    with open(source) as file:
        for line in file:
            record = line.split(sep=',')
            
            if not header_processed:
                header_processed = True
                continue
            # use_set = set()
            # if record[3] != '':
            #     for operating in str(record[3]).split(","):
            #         use_set.add(operating)
            # project_name: str
            # project_hash: str
            # line: int
            # module: str
            # call_name: str
            # call_name_long: str
            # is_test: bool
            # filename: str
            # url: str
            # call = Call(record[0], record[1], int(record[2]), record[3], record[4], record[5], bool(record[6]), record[7], record[8])
            call = Call("name","hash",int(record[2]), record[3], record[4], '', False, "filename", "github.com")
            # print(f"{record[10]} -> {record[10].lower().capitalize()} {'true'==record[10].lower().capitalize()} = {record}")
            # yield CallRecord(call, record[8], int(record[9]), record[10].lower().capitalize())
            yield CallRecord(call, record[8], int(record[9]), record[10])
                        
class TestCallIf(unittest.TestCase):

    def setUp(self):
        self.os_apis  = read_apis()
        self.filename = 'tests/unit/calls.csv'
        # self.filename = 'tests/unit/calls2.csv'
     
    def test_if_two_compare(self):
        pretty = 'https://github.com/ansible/ansible/blob/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
        raw = 'https://raw.githubusercontent.com/ansible/ansible/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
        self.assertEqual(self.pretty_to_raw(pretty), raw)
        
    def test_usages(self):
        for record in read_by_records(self.filename):
            with self.subTest(msg=f"{record.url_pretty}", record=record):
                if (self.find_problems(record.url_pretty)):
                    self.skipTest(f"problems with: {record.url_pretty}")
                code = self.read_code(record)
                file_compile = ast.parse(code)
                checkVisitor = CheckVisitor(self.os_apis)
                checkVisitor.visit(file_compile)
                
                present = record.call in checkVisitor.calls_context #se não estiver, tem risco
                risk = record.risk == 0 # zero representa que não tem risco; 1, que tem
                if (present!=risk):
                    # print(f'handle: {record.handle}, url: {record.url_pretty}')
                    print(f'{record.handle}; {record.url_pretty}')
                self.assertIn(record.call, checkVisitor.calls) 
                self.assertTrue(present == risk) 
                # self.assertIn(record.call, checkVisitor.calls_context) 
                # self.assertEqual(len(checkVisitor.calls_context), 1)
                # self.assertEqual(len(checkVisitor.calls), 1)
                
                # self.assertEqual(record.count, len(checkVisitor.usages), msg=record.url_pretty)
                # self.assertIn(record.usage, checkVisitor.usages, msg=record.url_pretty)
    
    def find_problems(self, url):
        problems = []
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