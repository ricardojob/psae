import unittest
import ast

from psae.capture import CheckVisitor, Usage, Call,  read_apis

class TestCallIf(unittest.TestCase):

    
    
    def setUp(self):
        self.os_apis = read_apis()
        
    
    def test_if_compare(self):
        code = """
import os 
import sys
@pytest.mark.skipif(sys.platform.startswith('darwin'), reason='macOS requires passlib')
def test_encrypt_with_rounds_no_passlib():
    pass
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        usage = Usage(4, 'sys.platform', {'darwin'})
        self.assertIn(usage, checkVisitor.usages) 
    
    def test_if_compare_and(self):
        code = """
import os 
import sys
@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason='macOS requires passlib')
def test_encrypt_with_rounds_no_passlib():
    pass
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        usage = Usage(4, 'sys.platform', {'darwin'})
        self.assertIn(usage, checkVisitor.usages) 
    
    def test_if_compare_not(self):
        code = """
import os 
import sys
@unittest.skipIf(sys.platform == "win32","Python on Windows doesn't have working os.chmod().",)
def test_notafile_error(self):
    with self.assertRaises( PermissionError if sys.platform == "win32" else IsADirectoryError):
        pass
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        # print(checkVisitor.usages)
        first_usage = Usage(4, 'sys.platform', {'win32'})
        second_usage = Usage(6, 'sys.platform', {'win32'})
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
        self.assertEqual(len(checkVisitor.usages), 2)
    
    def test_if_compare_skip(self):
        code = """
import os 
import sys
@unittest.skip
def test_notafile_error(self):
        pass
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 0)
        self.assertEqual(len(checkVisitor.calls), 0)
        self.assertEqual(len(checkVisitor.calls_context), 0)
    
    
    
    
if __name__ == '__main__':
    unittest.main()