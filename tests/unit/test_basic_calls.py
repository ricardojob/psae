import unittest

from psae.extract import ExtractPlatformSpecificDir
from psae.capture import Call

class TestCallForFunctions(unittest.TestCase):

    def test_simple(self):
        result_value = 4
        expect_value = 4
        self.assertEqual(result_value, expect_value)
    
    def test_length(self):
        directory = "../classes" # only one file
        extract = ExtractPlatformSpecificDir(directory)
        apis = extract.touch()
        self.assertEqual(3, len(apis))
    
    def test_contains(self):
        directory = "../classes" # only one file
        extract = ExtractPlatformSpecificDir(directory)
        apis = extract.touch()

        call_one = Call(project_name='name', project_hash='hash', line=5, module='asyncio', call_name='Task', call_name_long='', is_test=False, filename='/treat_custom_class.py', url='github.com') 
        call_two = Call(project_name='name', project_hash='hash', line=6, module='asyncio', call_name='wait', call_name_long='Task.wait', is_test=False, filename='/treat_custom_class.py', url='github.com') 
        call_three = Call(project_name='name', project_hash='hash', line=7, module='asyncio', call_name='Task', call_name_long='', is_test=False, filename='/treat_custom_class.py', url='github.com') 
        
        self.assertIn(call_one, apis)    
        self.assertIn(call_two, apis)    
        self.assertIn(call_three, apis)    

if __name__ == '__main__':
    unittest.main()