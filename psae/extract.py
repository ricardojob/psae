import os
import ast
import os.path
import logging
from typing import List
from capture import CheckVisitor, Call

logger = logging.getLogger(__name__)

def read_apis():
    import json
    file = open('psae/apis-os.json')
    return json.load(file)
 
class ExtractPlatformSpecificDir:
    # def __init__(self, directory, os_apis=read_apis()):
    #     self.directory = directory
    #     self.calls_apis = []  
    #     # self.os_apis = read_apis()
    #     self.os_apis = os_apis
    def __init__(self, project):
        self.project = project
        self.directory = project.directory
        self.calls_apis = []  
        # self.os_apis = read_apis()
        self.os_apis = project.read_apis()
        
    def touch(self) -> List[Call]: 
        # project_dir = "/Users/job/Documents/dev/doutorado/study/study-docs/input/classes"
        for python_file in self.__all_files(self.directory):
            try:
                if python_file.is_dir(): continue
                filename = str(python_file).replace(self.directory,"")
                logging.info(msg = f" Parse from: {str(python_file)}, filename: {str(filename)}")
                content = open(python_file).read()
                extract  = ExtractPlatformSpecific(self.os_apis)
                apis = extract.touch(content)
                for c in apis:
                    self.__map_to_call(filename, c)
                # return [print(f'names; hashs; {c.line}; {c.module}; {c.call_name}; {c.call_name_long}; {filename}') for c in apis]
                self.calls_apis.extend(apis)
            except SyntaxError as ex:
                # print('erro', python_file) 
                logger.error(
                    "Could not process python (file=%s)",
                    str(python_file),
                    exc_info=True,
                )
                # raise
        return self.calls_apis

    def __map_to_call(self, filename, c):
        c.filename = filename # _replace(filename=filename) 
        c.is_test = 'test' in filename # verify filename
        c.project_name = self.project.project_name
        c.project_hash = self.project.project_hash
        c.url = self.__build_url(c)
        
    def __build_url(self, c:Call):
    # def __build_url(project_name, project_hash, filename, line):
        # https://github.com/ansible/ansible/blob/4ea50cef23c3dc941b2e8dc507f37a962af6e2c8
        # /test/support/integration/plugins/modules/timezone.py#L107
        return f'https://github.com/{c.project_name}/blob/{c.project_hash}{c.filename}#L{c.line}'  
    def __all_files(self, dir, extension='.py'):
        """ List all files in dir. """
        from pathlib import Path
        path = Path(dir)
        files = []
        for file in path.rglob(pattern=f'*{extension}'):
            files.append(file)
        logging.info(msg = f" A total of {len(files)} python files were computed.")
        return files   
        
class ExtractPlatformSpecific:
    def __init__(self, os_apis):
        self.os_apis = os_apis   
        
    def touch(self, content)  -> List[Call]:
        file_compile = ast.parse(content)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        apis = checkVisitor.calls
        logging.info(msg = f" A total of {len(apis)} platform-specific apis were computed.")
        return apis
        
class WriteCSV:
    def __init__(self, output):
        self.output = output   
    
    def write(self, content):
        if self.output:
            self.write_to_file(content)    
        else:
            self.write_to_stdo(content)    
            
    def write_to_file(self, content):
        # print(content, self.output)
        # print(f'Output: {self.output}.csv, content: {content}')
        parent = os.path.dirname(self.output)
        print(f'Output: {self.output}, parent: {parent}, content: {content}')
        if parent != "":
            os.makedirs(parent, exist_ok=True)
        # with open(output, "a", encoding="utf-8") as file:
        #     utils.write_csv(
        #         entries, file, entries[0].__class__, not no_headers, repository_name
        #     )
    
    def write_to_stdo(self, content):
        [print(f'{c.project_name}; {c.project_hash}; {c.line}; {c.module}; {c.call_name}; {c.call_name_long}; {c.is_test} ; {c.filename}; {c.url}') for c in content]
        # print(content)
        # utils.write_csv(
        #     entries,
        #     sys.stdout,
        #     entries[0].__class__,
        #     not no_headers,
        #     repository_name,
        # )