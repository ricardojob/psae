from abc import ABC, abstractmethod
import os
import ast
import os.path
import logging
import csv
from typing import List
from psae.capture import CheckVisitor, Call

logger = logging.getLogger(__name__)

def read_apis():
    import json
    file = open('psae/apis-os.json')
    return json.load(file)
 
class ExtractPlatformSpecificDir:
    def __init__(self, project):
        self.project = project
        self.directory = project.directory
        self.calls_apis = []  
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
                    self.calls_apis.append(self.__map_to_call(filename, c))
            except SyntaxError as ex:
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
        
        call = []
        call.append(c.project_name)
        call.append(c.project_hash)
        call.append(c.line)
        call.append(c.module)
        call.append(c.call_name)
        # call.append(c.call_name_long)
        call.append(c.is_test) # verify filename
        call.append(c.filename)
        call.append(c.url)
        return call
        
    def __build_url(self, c:Call):
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
        
class Report(ABC):
    def __init__(self, output):
        self.output = output   
    
    @abstractmethod
    def write(self, content):
        """"""    
        
    def build(output):
        if output is None: #remote
            return ReportStdo()
        else: #local
            return ReportAPI(output)
        
        
class ReportAPI(Report):
    def __init__(self, output):
        super().__init__(output)
        self.call_headear = ['project_name','project_commit', 'line', 'module', 'call', 'is_test' ,'filename', 'url', 'risk']
    
    def write(self, content):
        parent = os.path.dirname(self.output)
        if parent != "":
            os.makedirs(parent, exist_ok=True)
        with open(self.output, 'w', encoding="utf-8") as file:
            write = csv.writer(file, delimiter =";")
            write.writerow(self.call_headear)
            write.writerows(content)
                        
class ReportStdo(Report):
    def __init__(self):
        super().__init__(None)
        
    def write(self, content):
        [print(f'{c[0]}; {c[1]}; {c[2]}; {c[3]}; {c[4]}; {c[5]}; {c[6]}; {c[7]}') for c in content]                    
    