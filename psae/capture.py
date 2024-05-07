from ast import Assign, Call
import ast
from dataclasses import dataclass
from pathlib import Path
import logging
from typing import Any, List, NamedTuple, Tuple

logger = logging.getLogger(__name__)

# DEBUG = True
DEBUG = False

@dataclass
class Call:
# class Call(NamedTuple):
    """A single Call's Platform-Specific API."""
    project_name: str
    project_hash: str
    line: int
    module: str
    call_name: str
    call_name_long: str
    is_test: bool
    filename: str
    url: str
    
    def make(line, module, call_name, call_name_long):
        return Call("name","hash",line, module, call_name, call_name_long, False, "filename", "github.com")

    def __eq__(self, other):
        if not isinstance(other, Call):
            return False
        return self.line == other.line and self.module == other.module and self.call_name == other.call_name and self.call_name_long == other.call_name_long
    def __hash__(self):
        return hash((self.line, self.module, self.call_name, self.call_name_long))
    
    
# class Call:
#     def __init__(self, line, module, call_name, call_name_long):
#         self.line = line
#         self.module = module
#         self.call_name = call_name
#         self.call_name_long = call_name_long
#     def __eq__(self, other):
#         if not isinstance(other, Call):
#             return False
#         return self.line == other.line and self.module == other.module and self.call_name == other.call_name and self.call_name_long == other.call_name_long
#     def __hash__(self):
#         return hash((self.line, self.module, self.call_name, self.call_name_long))

class CheckVisitor(ast.NodeVisitor):         
    def __init__(self, libs):   
        self.libs_os = libs
        self.modules = set()
        self.chamadas = dict()
        self.calls = set()
        
    def visit_Import(self, node):
        for name in node.names:
            module = name.name.split(".")[0]
            self.analyzing_modules(name, module, None)
            if module in self.libs_os:
                self.modules.add(module)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module is not None and node.level == 0:
            module = node.module.split(".")[0]
            [self.analyzing_modules(nam, module, nam.name) for nam in node.names ]    
            if module in self.libs_os:
                self.modules.add(module)
        self.generic_visit(node)  
    
    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            call_name = node.attr
            parent = node.value
            self.add_calls(call_name, parent)
            self.debug(f'- line: {node.lineno}, visit_Attribute: {call_name}, node: {node.value} ')
        self.generic_visit(node)
    
    def visit_Call(self, node: Call):
        call_name, parent = self.get_parent(node.func)
        self.add_calls(call_name, parent)
        self.debug(f'+ line: {node.lineno}, visit_Call: {call_name}, node: {node.func} ')    
        self.generic_visit(node)
    
    def visit_Assign(self, node: Assign):
        self.debug(f'v line: {node.lineno}, visit_Assign: {node}')    
        if isinstance(node.value, ast.Call):
            call_name, parent = self.get_parent(node.value)
            if "" != parent and not isinstance(parent, (bytes, bytearray)) and not isinstance(parent, str):
                self.debug(f'v is_call: {self.is_call_from_module(call_name, parent)} -> {call_name}, {parent} [before]')
                if self.is_call_from_module(call_name, parent):
                    if isinstance(node.targets[0], ast.Name):
                        target = node.targets[0].id
                        self.chamadas[target] = [parent.id, call_name]
                        self.debug(f'v module:{parent.id}, package: {call_name}, name: {call_name}, cham: {self.chamadas}') 
        self.generic_visit(node)

    def get_parent(self, node):
        call_name = ""
        parent = node
        while(not isinstance(parent, ast.Name)):
            if "" == parent or isinstance(parent, str) or type(parent) == str:
                break
            if isinstance(parent, (bytes, bytearray, int, float, complex)):
                break
            self.debug(f'g line: {parent.lineno}, visit_Assign: {call_name}, node: {parent} ')    
            if isinstance(parent, ast.Attribute):
                self.debug(f'g line: {parent.lineno}, rec {parent.attr} call: {call_name}')    
                if call_name == '':
                    call_name = parent.attr
                else:
                    call_name = parent.attr+'.'+call_name        
            if isinstance(parent, ast.Call):
                parent = parent.func
                continue
            if isinstance(parent, ast.BinOp):
                parent = parent.left #TODO: may be add bug
                continue
            if isinstance(parent, ast.Tuple):
                parent = parent.elts[0] #TODO: may be add bug
                continue
            if isinstance(parent, ast.IfExp):
                parent = parent.test #TODO: may be add bug
                continue
            if isinstance(parent, ast.ListComp):
                parent = parent.elt #TODO: may be add bug
                continue
            if isinstance(parent, (ast.BoolOp, ast.JoinedStr, ast.Dict)):
                if parent.values is None:
                    break
                if len(parent.values) == 0:
                    break
                parent = parent.values[0] #TODO: may be add bug
                continue
            # if isinstance(parent, ast.JoinedStr):
            #     parent = parent.values[0] #TODO: may be add bug
            #     continue
            # if isinstance(parent, ast.Dict):
            #     parent = parent.values[0] #TODO: may be add bug
            #     continue
            # self.debug(f'g line: {parent.lineno}, visit_Assign: {call_name}, node: {parent} [after]')    
            if not hasattr(parent, 'value'):
               break 
            parent = parent.value
            self.debug(f'g return:: call_name: {call_name} and parent: {parent}')    
        return call_name, parent
    
    def analyzing_modules(self, node, module, package):
        key = node.name
        if node.asname:
            key = node.asname
        self.debug(f'package:{node.name}, as: {node.asname} -> key: {key}, module:{module}')   
        self.chamadas[key] = [module, package] # package_name -> [package, module]
        self.debug(f'module:{module}, package: {package}, name: {key}, cham: {self.chamadas}') 
        
    def is_call_from_module(self, call_name, node):
        if not isinstance(node, ast.Name):
            return False
        if node is None or node.id is None:
            return False
        module_node = node.id
        self.debug(f"i call: module node:{module_node}")
        if not module_node in self.chamadas:
            return False
        module_name = self.chamadas[module_node][0]
        # lib_and_module = any(module_name in item for item in self.libs_os.values()) and (mod in self.libs_os)
        module_call = ""
        if module_name in self.chamadas:
            module_call = self.chamadas[module_name][0]
        self.debug(f"i call: module:{module_name}, mod_call: {module_call}, call: {call_name} is module : {module_name in self.libs_os}, is call: {module_call in self.libs_os}")
        if not module_name in self.libs_os and not module_call in self.libs_os:
            # if module_call in self.libs_os:
                # pass
            return False
        # self.debug(f"i call: afafasfa module :{module_name in self.libs_os}")
        # negative (p or q) -> not p and not q
        if module_call in self.libs_os:
            module_name = module_call
        if (not call_name in self.libs_os[module_name] and not len(self.libs_os[module_name])==0): 
            return False
        return True
    
    def is_member_of(self, module_name, member_name): #verifica se o módulo possui a funcão, método ou atributo
        import importlib, inspect
        if module_name == 'spwd': 
            if (member_name == "getspnam" or member_name =="getspall"):
                return True
            else: 
                return False
        module = importlib.import_module(module_name.strip())
        def is_member_of(obj, name):
            if name in inspect.getmembers(obj, (inspect.isfunction or inspect.ismethod)):
                return True
            if getattr(obj, name, None) is not None:
                return True
            if hasattr(obj, name): 
                return True
            return False
        if is_member_of(module, member_name):
            return True 
        for name, classs in inspect.getmembers(module, inspect.isclass):
            if name == member_name: 
                return True
            if is_member_of(classs, member_name):
                return True 
        return False
    
    def add_calls(self, call_name, node):
        if not self.is_call_from_module(call_name, node): 
            return
        # self.debug(f"> line: {node.lineno}, node: {module_node}, module: {module_name}, call: {call_name}")
        module_name = self.chamadas[node.id][0]
        if call_name == "":
            call_name = node.id
        
        call_name_long = ""    
        if not module_name in self.libs_os: #and module_name in self.chamadas:
            call_name_long = f"{module_name}.{call_name}" # para capturar com dot
            module_name = self.chamadas[module_name][0]
        
        if not self.is_member_of(module_name, call_name):
            return
        
        self.debug(f"> line: {node.lineno}, node: {node.id}, call: {call_name}, module: {module_name}")
        # self.calls.add(Call(node.lineno, module_name, call_name, call_name_long))
        self.calls.add(
            Call.make(node.lineno, module_name, call_name, call_name_long)
        )
    
    def debug(self, msg):
        if DEBUG:
            # print(f'[debug] {self}: {msg}')
            # print(f'[debug] {msg}')    
            logger.info(msg=msg
                # "Could not decode or validate workflow for %s (commit=%s, change_type=%s)",
                # f"{msg}",
                # exc_info=True,
            )         

def all_files(dir, extension='.py'):
    """ 
    List all files in dir
    """
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

if __name__ == '__main__':
    project_dir = "/Users/job/Documents/dev/doutorado/study/study-docs/input/classes"
    os_apis = read_apis()
    for python_file in all_files(project_dir):
        if python_file.is_dir(): continue
        filename = str(python_file).replace(project_dir,"")
        try:
            file_compile = ast.parse(open(python_file).read())
            checkVisitor = CheckVisitor(os_apis)
            checkVisitor.debug(f"parse from: {python_file}")
            checkVisitor.visit(file_compile)
            [print(f'name; hash; {c.line}; {c.module}; {c.call_name}; {c.call_name_long}; {filename}') for c in checkVisitor.calls]
            # call.append(project_name)
            #                 call.append(project_hash)
            #                 call.append(c.line)
            #                 call.append(c.module)
            #                 call.append(c.call_name)
            #                 call.append(filename)
            #                 call.append(build_url(project_name, project_hash, filename, c.line))
            #                 calls.append(call)
        except SyntaxError as ex:
            print('erro', python_file) 
 
"""        
    source = 
import asyncio
import platform
def exec_async_tasks(tasks):
    if platform.system() == "Windows":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    try:
        errors = loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        loop.close()
    return errors
    '''
    print(ast.dump(ast.parse(source)))
"""
    
"""
    def visit_Call(self, node: Call):
        # if isinstance(node, ast.Call):
        self.debug(f'+ linha: {node.lineno}, visit_Call: {node.func} ')    
        # self.debug(f'[c] - {node.func.value.value.id} , {node.keywords}, {node.lineno}')
        if isinstance(node.func, ast.Attribute):
            self.debug(f'visit_Call_attribute: {node.func.value}')    
            self.tratar_Name(node.func.value, node.func)
            # self.parse_attr(node.func)
        if isinstance(node.func, ast.Name):
            self.debug(f'visit_Call_name: {node.func.id}')  
            self.tratar_Name(node.func, node)
            # self.parse_attr(node.func)
        # for arg in node.args:   
        #     # self.debug(f'[parse_call_arg] {node.func.id} {arg}')    
        #     # if isinstance(arg, ast.Call):
        #     #     self.parse_call(arg)
        #     if isinstance(arg, ast.Constant):
        #         # self.razion['platform'] = arg.value
        #         # self.platform = arg.value
        #         self.debug(f'[p] call platform: {arg.value} ')
        self.generic_visit(node)
        
    def visit_Attribute(self, node):
        att = node.value
        if isinstance(att, ast.Name):
            self.debug(f"visit_Attribute context of Name: {node.value.id} ")
            self.tratar_Name(att, node)
        self.generic_visit(node)
    
    def tratar_Name(self, node, parent):
        self.debug(f'tratar_Name: {node}')
        # if isinstance(node, ast.Attribute):
        #     self.tratar_Name(node.value, node)
        if isinstance(node, ast.Name):
            if node.id and node.id in self.chamadas:
                mod = self.chamadas[node.id]
                if mod[0] in self.libs_os:
                    if (parent.attr in self.libs_os[mod[0]] or len(self.libs_os[mod[0]])==0):
                        self.debug(f"- linha: {node.lineno}, node:{node.id}, module: {mod[0]}, call: {parent.attr}, parent: {parent}")
            # self.debug(f"- linha: {node.lineno}, node:{node.id}, call: {parent.attr}, parent: {parent}")
    
    # Attribute(expr value, identifier attr, expr_context ctx)
    def parse_attr(self, attribute):
        # self.debug(f'[parse_attr] {attribute.value} ')
        if isinstance(attribute, ast.Name):
            self.debug(f'[parse_attr] {attribute.id} , {attribute}')
        #     self.razion['module'] = attribute.id
        #     self.razion['line'] = attribute.lineno
        #     self.razion['url'] = self.gerar_url(attribute.lineno)
        #     return
        
        if isinstance(attribute, ast.Attribute):
            self.parse_attr(attribute.value)
        # if isinstance(attribute.value, ast.Name):
        #     if attribute.value.id in self.chamadas:
        #         self.razion['module'] = self.chamadas[attribute.value.id][0]
        #     else:                 
        #         self.razion['module'] = attribute.value.id
        #     self.razion['line'] = attribute.lineno
        #     self.razion['url'] = self.gerar_url(attribute.lineno)
            
        # if not 'package' in self.razion:
        #     self.razion['package'] = attribute.attr
        # self.atts.append(attribute)
    """
           