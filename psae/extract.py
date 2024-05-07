import os
import ast
import os.path
import logging
from typing import List
from capture import CheckVisitor, Call

logger = logging.getLogger(__name__)

    
def all_files(dir, extension='.py'):
    """ List all files in dir. """
    from pathlib import Path
    path = Path(dir)
    files = []
    for file in path.rglob(pattern=f'*{extension}'):
        files.append(file)
    # [print(f) for f in files]
    return files

def read_apis():
    import json
    file = open('psae/apis-os.json')
    return json.load(file)
 
class ExtractPlatformSpecificDir:
    def __init__(self, directory):
        self.directory = directory
        self.calls_apis = []  
        self.os_apis = read_apis()
        
    def touch(self) -> List[Call]: # project_dir = "/Users/job/Documents/dev/doutorado/study/study-docs/input/classes"
        for python_file in all_files(self.directory):
            try:
                if python_file.is_dir(): continue
                filename = str(python_file).replace(self.directory,"")
                logging.info(msg = f" parse from: {str(python_file)}")
                content = open(python_file).read()
                extract  = ExtractPlatformSpecific(self.os_apis)
                apis = extract.touch(content)
                for c in apis:
                    c.filename = filename # _replace(filename=filename) 
                    c.is_test = 'test' in filename # verify filename
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
       
        
class ExtractPlatformSpecific:
    def __init__(self, os_apis):
        self.os_apis = os_apis   
        
    def touch(self, content)  -> List[Call]:
        file_compile = ast.parse(content)
        checkVisitor = CheckVisitor(self.os_apis)
        checkVisitor.visit(file_compile)
        return checkVisitor.calls
        
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
        print(f'Output: {self.output}.csv, parent: {parent}, content: {content}')
        if parent != "":
            os.makedirs(parent, exist_ok=True)
        # with open(output, "a", encoding="utf-8") as file:
        #     utils.write_csv(
        #         entries, file, entries[0].__class__, not no_headers, repository_name
        #     )
    
    def write_to_stdo(self, content):
        [print(f'{c.project_name}; hashs; {c.line}; {c.module}; {c.call_name}; {c.call_name_long}; {c.is_test} ; {c.filename}') for c in content]
        # print(content)
        # utils.write_csv(
        #     entries,
        #     sys.stdout,
        #     entries[0].__class__,
        #     not no_headers,
        #     repository_name,
        # )