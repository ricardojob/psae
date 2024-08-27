import unittest
import ast
import requests

from psae.capture import CheckVisitor, Usage, Call,  read_apis

class TestCallIf(unittest.TestCase):

    def setUp(self):
        self.os_apis = read_apis()
     
    def pretty_to_raw(self, pretty:str):    
        # pretty = 'https://github.com/ansible/ansible/blob/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
        # raw = 'https://raw.githubusercontent.com/ansible/ansible/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
        raw = pretty.replace("/blob/","/").replace("github.com/", "raw.githubusercontent.com/")
        return raw
        
    def test_if_two_compare(self):
        pretty = 'https://github.com/ansible/ansible/blob/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
        raw = 'https://raw.githubusercontent.com/ansible/ansible/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
        self.assertEqual(self.pretty_to_raw(pretty), raw)
   
    
    def test_psae_high(self):
        pretty_url = 'https://github.com/ricardojob/psae/blob/9b6b343cbff59d5dbe567c336657249c18aa93a6/tests/classes/on/treat_try_class.py#L50'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)

        first_usage =  Usage(23,'sys.platform', {'win32'}) 
        second_usage =  Usage(34,'sys.platform', {'win32'}) 
        third_usage =  Usage(44,'sys.platform', {'win32'})  
        
        first_call = Call('name', 'hash', 7, 'os', 'chown', '', False, 'filename', 'github.com', "low")
        second_call = Call('name', 'hash', 16, 'os', 'chown', '', False, 'filename', 'github.com', "low")
        third_call = Call('name', 'hash', 26, 'os', 'chown', '', False, 'filename', 'github.com', "low")
        fouth_call = Call('name', 'hash', 35, 'os', 'chown', '', False, 'filename', 'github.com', "low")
        fifth_call = Call('name', 'hash', 50, 'os', 'chown', '', False, 'filename', 'github.com', "high")
        
        self.assertEqual(len(checkVisitor.usages), 3)
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
        self.assertIn(third_usage, checkVisitor.usages) 
        
        self.assertIn(first_call, checkVisitor.calls) 
        self.assertIn(second_call, checkVisitor.calls) 
        self.assertIn(third_call, checkVisitor.calls) 
        self.assertIn(fouth_call, checkVisitor.calls) 
        self.assertIn(fifth_call, checkVisitor.calls) 
        self.assertIn(first_call, checkVisitor.calls_context) 
        self.assertIn(second_call, checkVisitor.calls_context) 
        self.assertIn(third_call, checkVisitor.calls_context) 
        self.assertIn(fouth_call, checkVisitor.calls_context) 
        self.assertNotIn(fifth_call, checkVisitor.calls_context) 
        self.assertEqual(len(checkVisitor.calls_context), 4)
        self.assertEqual(len(checkVisitor.calls), 5)
        
    
        
if __name__ == '__main__':
    unittest.main()