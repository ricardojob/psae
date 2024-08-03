import unittest
import ast

from psae.capture import CheckVisitor, Usage, Call,  read_apis

class TestCallIf(unittest.TestCase):
    def setUp(self):
        self.os_apis = read_apis()
        
    def test_call_simple(self):
        code = """
import os 
import sys
def with_if_compare():   
    print(os.getgid())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        first_call = Call('name', 'hash', 5, 'os', 'getgid', '', False, 'filename', 'github.com')
        self.assertIn(first_call, checkVisitor.calls) 
        self.assertEqual(len(checkVisitor.usages), 0)
        self.assertEqual(len(checkVisitor.calls), 1)
        self.assertEqual(len(checkVisitor.calls_context), 0)
    
    def test_call_if(self):
        code = """
import os 
import sys
def with_if_compare():   
    if sys.platform != "win32":
        print(os.fork())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        
        usage = Usage(5, 'sys.platform', {'win32'})
        first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(first_call, checkVisitor.calls_context) 
        self.assertIn(first_call, checkVisitor.calls) 
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls_context), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_if_not(self):
        code = """
import os 
import sys
def with_if_compare():   
    if not sys.platform.startswith("win"):
        print(os.fork())
                """
        # if not sys.platform.startswith("win"):
        # scpstat = subprocess.Popen(["/bin/sh", "-c", "command -v scp"]).wait()                
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        
        usage = Usage(5, 'sys.platform', {'win'})
        first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(first_call, checkVisitor.calls_context) 
        self.assertIn(first_call, checkVisitor.calls) 
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls_context), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
 
    def test_call_if_else(self):
        code = """
import os 
import sys
def with_if_compare():   
    if sys.platform.startswith("win"):
        pass
    else:
        print(os.fork())
                """
        # if not sys.platform.startswith("win"):
        # scpstat = subprocess.Popen(["/bin/sh", "-c", "command -v scp"]).wait()                
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        
        usage = Usage(5, 'sys.platform', {'win'})
        first_call = Call('name', 'hash', 8, 'os', 'fork', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(first_call, checkVisitor.calls_context) 
        self.assertIn(first_call, checkVisitor.calls) 
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls_context), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
    
        
    def test_call_if_and_out(self):
        code = """
import os 
import sys
def with_if_compare():   
    print(os.getgid())
    if sys.platform != "win32":
        print(os.fork())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        
        usage = Usage(6, 'sys.platform', {'win32'})
        first_call = Call('name', 'hash', 5, 'os', 'getgid', '', False, 'filename', 'github.com')
        second_call = Call('name', 'hash', 7, 'os', 'fork', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(first_call, checkVisitor.calls) 
        self.assertIn(second_call, checkVisitor.calls) 
        self.assertIn(second_call, checkVisitor.calls_context)
        self.assertNotIn(first_call, checkVisitor.calls_context)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 2)
        self.assertEqual(len(checkVisitor.calls_context), 1)
    
    def test_call_if_simple(self):
            code = """
import os 
def with_if_compare():   
    if a > 1:
        print(os.fork())
                """
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            
            first_call = Call('name', 'hash', 5, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertNotIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertEqual(len(checkVisitor.usages), 0)
            self.assertEqual(len(checkVisitor.calls_context), 0)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_if_nested_internal(self):
        code = """
import os 
def with_if_compare():   
    if a > 1:
        if sys.platform != "win32":
            print(os.fork())
            """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        usage = Usage(5, 'sys.platform', {'win32'})
        first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
        self.assertIn(first_call, checkVisitor.calls_context) 
        self.assertIn(first_call, checkVisitor.calls) 
        self.assertIn(usage, checkVisitor.usages) 
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls_context), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_if_nested(self):
            code = """
import os 
def with_if_compare():   
    if sys.platform != "win32":
        if a > 1:
            print(os.fork())
                """
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            usage = Usage(4, 'sys.platform', {'win32'})
            first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertIn(usage, checkVisitor.usages) 
            self.assertEqual(len(checkVisitor.usages), 1)
            self.assertEqual(len(checkVisitor.calls_context), 1)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_try(self):
            code = """
import os 
def with_if_compare():   
    try:
        print(os.fork())
    except OSError:
        pass
                """
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            first_call = Call('name', 'hash', 5, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertEqual(len(checkVisitor.usages), 0)
            self.assertEqual(len(checkVisitor.calls_context), 1)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_try_nested(self):
            code = """
import os 
def with_if_compare():   
    try:
        try:
            print(os.fork())
        except OSError:
            pass
    except OSError:
        pass
                """
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertEqual(len(checkVisitor.usages), 0)
            self.assertEqual(len(checkVisitor.calls_context), 1)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_try_if(self):
            code = """
import os 
def with_if_compare():   
    try:
        if a > 1:
            print(os.fork())
    except OSError:
        pass
                """
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertEqual(len(checkVisitor.usages), 0)
            self.assertEqual(len(checkVisitor.calls_context), 1)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_if_try(self):
            code = """
import os 
def with_if_compare():   
    if a > 1:
        try:
            print(os.fork())
        except OSError:
            pass
                """
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertEqual(len(checkVisitor.usages), 0)
            self.assertEqual(len(checkVisitor.calls_context), 1)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_if_usage_try(self):
            code = """
import os 
import sys 
def with_if_compare():   
    if sys.platform != "win32":
        try:
            print(os.fork())
        except OSError:
            pass
                """
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            usage = Usage(5, 'sys.platform', {'win32'})
            first_call = Call('name', 'hash', 7, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertIn(usage, checkVisitor.usages) 
            self.assertEqual(len(checkVisitor.usages), 1)
            self.assertEqual(len(checkVisitor.calls_context), 1)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_usage_except(self):
            code = """
import os 
import sys 
def with_if_compare():   
    try:
        pass
    except OSError:
        print(os.fork())
                """
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            first_call = Call('name', 'hash', 8, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertNotIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertEqual(len(checkVisitor.usages), 0)
            self.assertEqual(len(checkVisitor.calls_context), 0)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_usage_except_if(self):
            code = """
import os 
import sys 
def with_if_compare(): 
    if sys.platform != "win32":  
        try:
            pass
        except OSError:
            print(os.fork())
                """
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            usage = Usage(5, 'sys.platform', {'win32'})
            first_call = Call('name', 'hash', 9, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertIn(usage, checkVisitor.usages) 
            self.assertEqual(len(checkVisitor.usages), 1)
            self.assertEqual(len(checkVisitor.calls_context), 1)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_decorator(self):
            code = """
import os 
import sys
@pytest.mark.skipif(not sys.platform.startswith('darwin'), reason='macOS requires passlib')
def test_encrypt_with_rounds_no_passlib():
    print(os.fork())
"""
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            usage = Usage(4, 'sys.platform', {'darwin'})
            first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertIn(usage, checkVisitor.usages) 
            self.assertEqual(len(checkVisitor.usages), 1)
            self.assertEqual(len(checkVisitor.calls_context), 1)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_decorator_not_compare(self):
            code = """
import os 
import sys
@pytest.mark.skip(reason='macOS requires passlib')
def test_encrypt_with_rounds_no_passlib():
    print(os.fork())
"""
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertNotIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertEqual(len(checkVisitor.usages), 0)
            self.assertEqual(len(checkVisitor.calls_context), 0)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_call_decorator_not_declared(self):
            code = """
import os 
import sys
@unittest.skip
def test_encrypt_with_rounds_no_passlib():
    print(os.fork())
"""
            file_compile = ast.parse(code)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
            self.assertNotIn(first_call, checkVisitor.calls_context) 
            self.assertIn(first_call, checkVisitor.calls) 
            self.assertEqual(len(checkVisitor.usages), 0)
            self.assertEqual(len(checkVisitor.calls_context), 0)
            self.assertEqual(len(checkVisitor.calls), 1)
    
    
if __name__ == '__main__':
    unittest.main()