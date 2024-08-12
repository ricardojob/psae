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
def with_if_compare():   
    if sys.platform != "win32":
        print(os.fork())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        usage = Usage(5, 'sys.platform', {'win32'})
        call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls) 
    
    def test_if_compare_left(self):
        code = """
import os 
import sys 
def with_if_compare_left():    
    if "linux" == sys.platform:
        print(os.getgid())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        usage = Usage(5, 'sys.platform', {'linux'})
        call = Call('name', 'hash', 6, 'os', 'getgid', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls) 
    
    def test_if_compare_not(self):
        code = """
import os 
import sys
def with_if_compare_not():   
    if not sys.platform != "win32":
        print(os.fork())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        usage = Usage(5, 'sys.platform', {'win32'})
        call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls) 
        
    def test_if_compare_and(self):
        code = """
import os 
import sys 
def with_if_compare_and(key):    
    if sys.platform != "win32" and key == b"Content-Type":
        print(os.fork())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        usage = Usage(5, 'sys.platform', {'win32'})
        call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls) 
    
    def test_if_compare_or(self):
        code = """
import os 
import sys 
def with_if_compare_or(key):    
    if sys.platform != "win32" or key == b"Content-Type":
        print(os.fork())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        usage = Usage(5, 'sys.platform', {'win32'})
        call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls) 
    
    
    def test_if_two_compare(self):
        code = """
import os 
import sys 
def with_if_two_compare():    
    if sys.platform != "win32":
        print(os.fork())
    if "linux" == sys.platform:
        print(os.getgid())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 2)
        self.assertEqual(len(checkVisitor.calls), 2)
        first_usage = Usage(5, 'sys.platform', {'win32'})
        second_usage = Usage(7, 'sys.platform', {'linux'})
        first_call = Call('name', 'hash', 6, 'os', 'fork', '', False, 'filename', 'github.com')
        second_call = Call('name', 'hash', 8, 'os', 'getgid', '', False, 'filename', 'github.com')
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
        self.assertIn(first_call, checkVisitor.calls) 
        self.assertIn(second_call, checkVisitor.calls) 
    
    def test_if_compare_tuple(self):
        code = """
import os 
import sys 
def with_if_compare_tuple():    
    if sys.platform in ('linux', 'win32'):
        print(os.getgid())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        usage = Usage(5, 'sys.platform', {'win32', 'linux'})
        call = Call('name', 'hash', 6, 'os', 'getgid', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls)     
    
    def test_if_compare_list(self):
        code = """
import os 
import sys 
def with_if_compare_list():    
    if sys.platform in ['linux', 'win32']:
        print(os.getgid())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        usage = Usage(5, 'sys.platform', {'win32', 'linux'})
        call = Call('name', 'hash', 6, 'os', 'getgid', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls)     
    
    def test_if_call(self):
        code = """
import os 
import sys 
def with_if_call():    
    if sys.platform.startswith("linux"):
        print(os.chown)
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        usage = Usage(5, 'sys.platform', {'linux'})
        call = Call('name', 'hash', 6, 'os', 'chown', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls)     
    
    def test_if_call_compare_platform(self):
        code = """
import os 
import platform
def with_if_call_compare_platform():    
    if platform.system() == 'Linux':
        print(os.chown)
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        usage = Usage(5, 'platform.system', {'Linux'})
        call = Call('name', 'hash', 6, 'os', 'chown', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls)         
    
    def test_if_call_compare(self):
        code = """
import os 
import sys
def with_if_call_compare():    
     if sys.platform.startswith("linux") == True:
         print(os.chown)
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        usage = Usage(5, 'sys.platform', {'linux'})
        call = Call('name', 'hash', 6, 'os', 'chown', '', False, 'filename', 'github.com')
        self.assertIn(usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls)     
        # print(checkVisitor.usages)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
    
    def test_if_nested(self):
        code = """
import os 
import sys
def with_if_nested():    
     if sys.platform != "win32":
         if sys.platform.startswith("darwin"):
             print(os.getgid())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 2)
        self.assertEqual(len(checkVisitor.calls), 1)
        first_usage = Usage(5, 'sys.platform', {'win32'})
        second_usage = Usage(6, 'sys.platform', {'darwin'})
        call = Call('name', 'hash', 7, 'os', 'getgid', '', False, 'filename', 'github.com')
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls)     
    
    def test_if_args(self):
        code = """
import os 
import platform
def with_if_args():               
    if any(platform.win32_ver()):
        print(os.getgid())
                """
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 1)
        first_usage = Usage(5, 'platform.win32_ver', set())
        call = Call('name', 'hash', 6, 'os', 'getgid', '', False, 'filename', 'github.com')

        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(call, checkVisitor.calls)     
    
    def test_if_assert(self):
        code = """
import os 
import platform
def test_user_agent():
    res = user_agent.user_agent()
    assert platform.system() in res
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        # self.assertEqual(len(checkVisitor.usages), 1) # removido compare
        self.assertEqual(len(checkVisitor.calls), 0)
        first_usage = Usage(6, 'platform.system', set())

        self.assertIn(first_usage, checkVisitor.usages) 
    
    def test_if_subscript(self):
        code = """
import os 
import platform
def test_user_agent():
    if sys.platform[:5] == 'linux':
        pass
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 0)
        first_usage = Usage(5, 'sys.platform', {'linux'})

        self.assertIn(first_usage, checkVisitor.usages) 
    
    def test_if_hasattr(self):
        code = """
import os 
def test_user_agent():
    if hasattr(os, "register_at_fork"):
        os.register_at_fork()
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        call = Call('name', 'hash', 5, 'os', 'register_at_fork', '', False, 'filename', 'github.com')
        
        self.assertEqual(len(checkVisitor.usages), 0)
        self.assertEqual(len(checkVisitor.calls), 1)
        self.assertEqual(len(checkVisitor.calls_context), 1)
        self.assertIn(call, checkVisitor.calls)     
        self.assertIn(call, checkVisitor.calls_context)     

    def test_if_assign(self):
        code = """
import os 
import sys
def test_getwindowsversion():
    macos_version = platform.mac_ver()[0]
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 0)
        first_usage = Usage(5, 'platform.mac_ver', set())

        self.assertIn(first_usage, checkVisitor.usages) 
    
    def test_if_call_in(self):
        code = """
import os 
import sys
def test_getwindowsversion():
    if 'windows' in platform.platform().lower():
        pass
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 0)
        first_usage = Usage(5, 'platform.platform', {'windows'})

        self.assertIn(first_usage, checkVisitor.usages) 
        
    def test_if_assert_assign(self):
        code = """
import os 
import sym
def test_getwindowsversion():
    # platforms=platform.platform
    # dict(platform=platform.platform())
    assert sys_info_instance._system == dict(platformj=platform.platform())
"""
        # print(ast.dump(ast.parse('dict(platform=platform.platform())', mode='eval'), indent=4))
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        # self.assertEqual(len(checkVisitor.usages), 1) # removido compare
        self.assertEqual(len(checkVisitor.calls), 0)
        # first_usage = Usage(5, 'platform.platform', {})
        first_usage = Usage(7, 'platform.platform', set())
        self.assertIn(first_usage, checkVisitor.usages) 
    
    def xtest_if_subscript(self):
        code = """
import os 
import sys
def test_user_agent():
    if (sys.platform == 'win32' or sys.platform == 'cygwin'):
        pass
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 2)
        self.assertEqual(len(checkVisitor.calls), 0)
        first_usage = Usage(5, 'sys.platform', {'win32'})
        second_usage = Usage(5, 'sys.platform', {'cygwin'})

        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 

# problems
    def test_if_call_compare_platform_calls(self):
        code = """
import os 
import platform
def with_if_call_compare_platform():    
    if platform.system().lower() == 'windows':
        pass
"""
        # self.os_apis =  dict()
        # self.os_apis['sys'] = [ 'platform', 'getwindowsversion']
        # self.os_apis['os'] = ['name', 'supports_bytes_environ', 'name']
        # self.os_apis['platform'] = ['platform', 'system', 'version', 'uname','win32_edition','win32_ver','win32_is_iot','mac_ver','libc_ver', 'freedesktop_os_release']
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        usage = Usage(5, 'platform.system', {'windows'})
        self.assertIn(usage, checkVisitor.usages) 
                
    def test_if_osname(self):
        code = """
import os 
import platform
def test_user_agent():
    if not osname or osname == os.name:
        pass
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 0)
        first_usage = Usage(5, 'os.name', set())

        self.assertIn(first_usage, checkVisitor.usages) 
    
    def test_if_joinstr_formatted(self):
        code = """
import os 
import platform
def test_user_agent():
    assert logs[6][2] == f"platform: {platform.platform()}"
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 0)
        first_usage = Usage(5, 'platform.platform', set())

        self.assertIn(first_usage, checkVisitor.usages) 

    def test_if_joinstr_formatted(self): # 463 -- 469 commented lines
        code = """
import os 
import sys
def test_getwindowsversion():
    if sys.getwindowsversion()[:2] >= (6, 0):
        pass
"""
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertEqual(len(checkVisitor.calls), 0)
        first_usage = Usage(5, 'sys.getwindowsversion', {'6','0'})

        self.assertIn(first_usage, checkVisitor.usages) 

        
if __name__ == '__main__':
    unittest.main()