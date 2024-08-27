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
            
    def test_ansible_timezone(self):
        pretty_url = 'https://github.com/ansible/ansible/blob/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)

        first_usage =  Usage(107,'platform.system', {'Linux'})
        second_usage =  Usage(131, 'platform.platform', {'^(Free|Net|Open)BSD'})
        third_usage =  Usage(118, 'platform.version', {'^joyent_.*Z'})
        fourth_usage =  Usage(133, 'platform.system', {'AIX'})
        fifth_usage =  Usage(129, 'platform.system', {'Darwin'})

        self.assertEqual(len(checkVisitor.usages), 5)
                
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
        self.assertIn(third_usage, checkVisitor.usages) 
        self.assertIn(fourth_usage, checkVisitor.usages) 
        self.assertIn(fifth_usage, checkVisitor.usages) 
    
    def test_youtube_dl_test_utils(self):
        pretty_url = 'https://github.com/ytdl-org/youtube-dl/blob/213d1d91bfc4a00fefc72fa2730555d51060b42d/test/test_utils.py#L257'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)

        first_usage =  Usage(213,'sys.platform', {'win32'})
        second_usage =  Usage(257, 'sys.platform', {'win32'})
        
        self.assertEqual(len(checkVisitor.usages), 2)
                
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
    
    def test_django_test_extraction(self):
        pretty_url = 'https://github.com/django/django/blob/2eb1f37260f0e0b71ef3a77eb5522d2bb68d6489/tests/i18n/test_extraction.py#L70'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        
        first_usage =  Usage(70,'os.name', {'nt'})
        second_usage =  Usage(1034,'os.name', {'nt'})
        
        self.assertEqual(len(checkVisitor.usages), 2)
                
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
    
    def test_django_test_fileresponse(self):
        pretty_url = 'https://github.com/django/django/blob/2eb1f37260f0e0b71ef3a77eb5522d2bb68d6489/tests/responses/test_fileresponse.py#L157'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        
        first_usage =  Usage(157,'sys.platform', {'win32'})
        second_usage =  Usage(233,'sys.platform', {'win32'})
        
        self.assertEqual(len(checkVisitor.usages), 2)
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
    
    def test_scrapy_asyncio_enabled_reactor_same_loop(self):
        pretty_url = 'https://github.com/scrapy/scrapy/blob/96033ce5a7f857942e3c6d488c8aab5b4aa03295/tests/CrawlerProcess/asyncio_enabled_reactor_same_loop.py#L7'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        
        first_usage =  Usage(7,'sys.platform', {'win32'})
        # first_usage =  Usage(7,'sys.platform', {'win32', 8, 3})

        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertIn(first_usage, checkVisitor.usages) 
    
    def test_faceswap_sysinfo_test(self):
        pretty_url = 'https://github.com/deepfakes/faceswap/blob/216ef387636eb7b84819c1b77d9a2f631ed97ab5/tests/lib/sysinfo_test.py#L54'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        
        first_usage =  Usage(54,'platform.platform', {})
        second_usage =  Usage(55,'platform.system', {})
        third_usage =  Usage(92,'platform.system', {})
        fourth_usage =  Usage(99,'platform.system', {})
        fifth_usage =  Usage(106,'platform.system', {})
        
        self.assertEqual(len(checkVisitor.usages), 5)
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
        self.assertIn(third_usage, checkVisitor.usages) 
        self.assertIn(fourth_usage, checkVisitor.usages) 
        self.assertIn(fifth_usage, checkVisitor.usages) 
    
    def test_rich_test_win32_console(self):
        pretty_url = 'https://github.com/textualize/rich/blob/076e0d208eb0b4e74cd8639e11a558b9319bd799/tests/test_win32_console.py#L28'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)

        first_usage =  Usage(10,'sys.platform', {'win32'})
        second_usage =  Usage(28,'sys.platform', {'win32'})
        
        self.assertEqual(len(checkVisitor.usages), 2)
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
    
    def test_numpy_test_array_interface(self):
        pretty_url = 'https://github.com/numpy/numpy/blob/2ef217d279d13afa2399efee864b9f11f4096aa7/numpy/core/tests/test_array_interface.py#L13'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)

        first_usage =  Usage(13,'sys.platform', {'linux'})
        
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertIn(first_usage, checkVisitor.usages) 
    
    def test_numpy_test_array_from_pyobj(self):
        pretty_url = 'https://github.com/numpy/numpy/blob/2ef217d279d13afa2399efee864b9f11f4096aa7/numpy/f2py/tests/test_array_from_pyobj.py#L164'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)

        # first_usage =  Usage(164,'sys.platform', {'linux'}) 
        # second_usage =  Usage(165,'platform.system', {'Darwin', 'arm'}) 
        first_usage =  Usage(164,'sys.platform', {'linux'}) 
        second_usage =  Usage(165,'platform.system', {'Darwin', 'arm'}) 
        self.assertEqual(len(checkVisitor.usages), 2)
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
    
    def test_numpy_extbuild(self):
        pretty_url = 'https://github.com/numpy/numpy/blob/2ef217d279d13afa2399efee864b9f11f4096aa7/numpy/testing/_private/extbuild.py#L195'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)

        first_usage =  Usage(183,'sys.platform', {'win32'}) 
        second_usage =  Usage(186,'sys.platform', {'linux'}) 
        third_usage =  Usage(193,'sys.platform', {'win32'}) 
        fourth_usage =  Usage(195,'sys.platform', {'darwin'}) 
        
        self.assertEqual(len(checkVisitor.usages), 4)
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
        self.assertIn(third_usage, checkVisitor.usages) 
        self.assertIn(fourth_usage, checkVisitor.usages) 
    
    def test_numpy_utils(self):
        pretty_url = 'https://github.com/numpy/numpy/blob/2ef217d279d13afa2399efee864b9f11f4096aa7/numpy/testing/_private/utils.py#L150'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        

        first_usage =  Usage(150,'os.name', {'nt'}) 
        second_usage =  Usage(185,'sys.platform', {'linux'}) 
        third_usage =  Usage(207,'sys.platform', {'linux'}) 
        fourth_usage =  Usage(2521,'sys.platform', {'linux'}) 
        
        self.assertEqual(len(checkVisitor.usages), 4)
        self.assertIn(first_usage, checkVisitor.usages) 
        self.assertIn(second_usage, checkVisitor.usages) 
        self.assertIn(third_usage, checkVisitor.usages) 
        self.assertIn(fourth_usage, checkVisitor.usages) 
    
    def test_gooey_test_chooser_results(self):
        pretty_url = 'https://github.com/chriskiehl/gooey/blob/be4b11b8f27f500e7326711641755ad44576d408/gooey/tests/test_chooser_results.py#L29'
        raw_url = self.pretty_to_raw(pretty_url)
        code = requests.get(raw_url).content
        file_compile = ast.parse(code)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        

        first_usage =  Usage(29,'os.name', {}) 
        
        self.assertEqual(len(checkVisitor.usages), 1)
        self.assertIn(first_usage, checkVisitor.usages) 
             
    # def test_faceswap_sysinfo_test(self):
    #     pretty_url = 'https://github.com/deepfakes/faceswap/blob/216ef387636eb7b84819c1b77d9a2f631ed97ab5/tests/lib/sysinfo_test.py#L54'
    #     raw_url = self.pretty_to_raw(pretty_url)
    #     code = requests.get(raw_url).content
    #     file_compile = ast.parse(code)
    #     checkVisitor = CheckVisitor(self.os_apis)
    #     checkVisitor.visit(file_compile)
        

    #     first_usage =  Usage(29,'os.name', {}) 
        
    #     self.assertEqual(len(checkVisitor.usages), 1)
    #     self.assertIn(first_usage, checkVisitor.usages) 
        
        
        # Usage(line=7, api='sys.platform', platforms={'win32'}) not found in 
        # {Usage(line=99, api='platform.system', platforms={'_is_macos', 'darwin'}), 
        #  Usage(line=54, api='platform.platform', platforms={'_system', '_configs', '_state_file'}), 
        #  Usage(line=106, api='platform.system', platforms={'windows', '_is_windows'}), 
        #  Usage(line=55, api='platform.system', platforms=set()), 
        #  Usage(line=92, api='platform.system', platforms={'_python', '_is_conda', '_cuda_check', 'conda', '_gpu', '_encoding', 'linux', 'conda-meta', '_is_linux'})}
    
        
if __name__ == '__main__':
    unittest.main()