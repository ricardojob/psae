from ast import Assign, Call
import ast
from dataclasses import dataclass
from pathlib import Path
import logging
# from typing import Any, List, NamedTuple, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Call:
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

@dataclass
# @dataclass(unsafe_hash=True)
# @dataclass(frozen=True, eq=True, unsafe_hash=True)
class Usage:
    """A single usage API to Identify OS."""
    line: int
    api: str
    platforms: set
    # def __init__(self, line:int, api:str, platforms:set) -> None:
    #     self.line = line
    #     self.api = api
    #     self.platforms = platforms
    
    def make(line, api):
        return Usage(line, api, set())

    def __eq__(self, other):
        if not isinstance(other, Usage):
            return False
        return self.line == other.line and self.api == other.api #and self.platforms == other.platforms
    def __hash__(self):
        return hash((self.line, self.api))
        # return hash((self.line, self.api, self.platforms))
    
class CheckVisitor(ast.NodeVisitor):         
    def __init__(self, libs, debug=False):   
        self.libs_os = libs
        self.modules = set()
        self.chamadas = dict()
        self.calls = set()
        self.calls_context = set()
        self.container = dict()
        self.DEBUG = debug
        # self.p = None
        
        # self.platforms = set()
        self.usage = Usage.make(0, '')
        self.usages = set()  
        self.decorators = ['pytest.mark.skipif', 'mark.skipif', 'skipif', 'pytest.mark.xfail', 'mark.xfail' ,'xfail', 'unittest.skipUnless','skipUnless', 'unittest.skipIf', 'skipIf']  
        
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
        # self.capture_bool(node)   
        self.generic_visit(node)
    
    def visit_Assign(self, node: Assign):
        self.debug(f' line: {node.lineno}, visit_Assign: {node}, value: {node.value}, targets: {node.targets}')    
        if isinstance(node.value, ast.Call):
            call_name, parent = self.get_parent(node.value)
            if "" != parent and not isinstance(parent, (bytes, bytearray)) and not isinstance(parent, str):
                self.debug(f'is_call: {self.is_call_from_module(call_name, parent)} -> {call_name}, {parent} [before]')
                if self.is_call_from_module(call_name, parent):
                    if isinstance(node.targets[0], ast.Name):
                        target = node.targets[0].id
                        self.chamadas[target] = [parent.id, call_name]
                        self.debug(f'module:{parent.id}, package: {call_name}, name: {call_name}, cham: {self.chamadas}') 
        for value in node.targets: #  current_os = platform.system()
            self.capture_bool(value)
        if isinstance(node.value, ast.Subscript):
            self.capture_bool(node.value.value) #current_os = platform.system()
        if isinstance(node.value, ast.Attribute):
            self.capture_bool(node.value)
        self.generic_visit(node)

    def get_parent(self, node):
        call_name = ""
        parent = node
        while(not isinstance(parent, ast.Name)):
            if "" == parent or isinstance(parent, str) or type(parent) == str:
                break
            if isinstance(parent, (bytes, bytearray, int, float, complex)):
                break
            self.debug(f'get_parent_line: {parent.lineno}, visit_Assign: {call_name}, node: {parent} ')    
            if isinstance(parent, ast.Attribute):
                self.debug(f'get_parent_line: {parent.lineno}, rec {parent.attr} call: {call_name}')    
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
    
    def is_declared_apis(self):
        if not self.modules:  return False 
        if not set(self.libs_os.keys()).intersection(self.modules): return False
        return True
    
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
        # self.debug(f"> begin:line: {node.lineno}, node: {node}, call: {call_name}")
        if not self.is_call_from_module(call_name, node): 
            return
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
        self.debug(f"add_calls:container: {self.container}, p: self.p ")
        # print(f"container: {self.container} \nusage: {self.usage} ")
        # self.usages.add(self.usage)
        # self.calls.add(Call(node.lineno, module_name, call_name, call_name_long))
        self.calls.add(
            Call.make(node.lineno, module_name, call_name, call_name_long)
        )
        nested = self.container.get('context','')
        if nested and nested!= "" and "yes" in nested:
            self.debug(f"add_calls:container:context: {self.container}, p: self.p ")
            self.calls_context.add(
                Call.make(node.lineno, module_name, call_name, call_name_long)
            )
    
    def debug(self, msg):
        if self.DEBUG:
            # logger.info(msg=msg)         
            print(msg)         
    
    def visit_FunctionDef(self, node):
        self.funcao = node.name
        self.debug(f"visit_FunctionDef:begin: {node.name}: {self.container}")        
        ant = self.container.get('function','')
        self.container['function'] = f"{ant}/{node.name}"
        # nested_function = self.container.get('nested_function','')
        # self.container['nested_function'] = f"{nested_function}/{node.name}"
        self.parse_decorator(node)
        self.generic_visit(node)
        self.container['function'] = f"{ant}"  
        self.debug(f"visit_FunctionDef:end: {node.name}: {self.container}")           
        self.clear_container() 

    def clear_container(self):
        if (self.container.get('function','') == "" 
            # and self.container.get('context','') !="" 
            and self.container.get('decorator','') ==""
            and self.container.get('conditional','') =="" 
            and self.container.get('class','') =="" 
            and self.container.get('nested','') =="" 
            and self.container.get('except','') =="") : 
            # self.container['conditional'] = ""   
            self.container['nested'] = ""   
            # self.container['compare'] = ""   
            self.container['current'] = ""   
            self.container['context'] = ""   
            # self.container['except'] = ""               
        
    # AsyncFunctionDef(identifier name, arguments args,stmt* body, expr* decorator_list, expr? returns,string? type_comment)
    def visit_AsyncFunctionDef(self, node):
        self.funcao = node.name
        self.debug(f"visit_AsyncFunctionDef:begin: {node.name}: {self.container}")        
        ant = self.container.get('function','')
        self.container['function'] = f"{ant}/{node.name}"
        self.parse_decorator(node)
        self.generic_visit(node)    
        self.container['function'] = f"{ant}"   
        self.debug(f"visit_AsyncFunctionDef:end: {node.name}: {self.container}")
        self.clear_container() 

        # if (self.container.get('function','') == ""): 
        #     self.debug(f"visit_AsyncFunctionDef:removed: {node.name}: {self.container}")
        #     self.container['conditional'] = ""   
        #     self.container['nested'] = ""   
        #     self.container['compare'] = ""   
        #     self.container['current'] = ""   
        #     self.container['context'] = ""   
        #     self.container['except'] = ""   
        
        # visit_Try:container: {'conditional': '', 'nested': '/try', 'function': '/_run_test_case', 'decorator': '', 'compare': '', 'current': '/try/if', 'context': 'yes', 'class': '', 'excepthandler': {'Timeout'}, 'except': ''}


    # ClassDef(identifier name,expr* bases,keyword* keywords,stmt* body,expr* decorator_list)
    def visit_ClassDef(self, node):
        self.classe = node.name
        self.funcao = ""
        ant = self.container.get('class','')
        self.container['class'] = f"{ant}/{node.name}"
        self.parse_decorator(node)
        self.generic_visit(node)
        self.container['class'] = f"{ant}"
           
    def visit_Compare(self, node):
        self.debug(f'visit_Compare begin: {node}')
        # for compare in node.comparators:
        #     self.capture_bool(compare)
        self.capture_bool(node)
        self.container['compare'] = "/cp"
        anterior = self.container.get('nested','')
        self.container['nested'] = f"{anterior}/cp"
        self.generic_visit(node)
        self.container['compare'] = ""
        self.container['nested'] = f"{anterior}"
        self.debug(f'visit_Compare end: {node}')
        
    def visit_IfExp(self, node):
        self.debug(f'visit_IfExp begin: line:{node.lineno} -> {node}, test: {node.test}')
        # if isinstance(node.test, ast.Compare):
        #     self.capture_compare(node.test)
        # if isinstance(node.test, ast.Call):
        #     self.capture_call(node.test)
        # self.capture_bool(node.test)
        # self.p = node
        # anterior = self.container.get('conditional','')
        self.container['conditional'] = "/if"
        # self.capture_bool(node.test)
        anterior = self.container.get('nested','')
        self.container['nested'] = f"{anterior}/if"
        self.capture_bool(node.test)
        self.generic_visit(node)
        # self.p = None
        self.container['conditional'] = ""
        # self.debug(f'visit_IfExp:container: {self.container}')
        nested = self.container.get('nested','')
        current = self.container.get('current','')
        tries = self.container.get('except','')
        if (nested==current and tries==""):
            self.container['context'] = ""
            self.container['current'] = f"{anterior}"
        self.container['nested'] = f"{anterior}"
        self.debug(f'visit_IfExp finish: {node}')
        self.usage = Usage.make(0, '')
    
    def visit_If(self, node):
        self.debug(f'visit_IfExp begin: line:{node.lineno} -> {node}, test: {node.test}')
        # self.capture_bool(node.test)
        # self.p = node
        # anterior = self.container.get('conditional','')
        self.container['conditional'] = "/if"
        # self.capture_bool(node.test)
        anterior = self.container.get('nested','')
        self.container['nested'] = f"{anterior}/if"
        self.capture_bool(node.test)
        self.debug(f'visit_If:container:generic_visit: {self.container}')
        self.generic_visit(node)
        # self.p = None
        self.container['conditional'] = ""
        self.debug(f'visit_If:container: {self.container}')
        nested = self.container.get('nested','')
        current = self.container.get('current','')
        tries = self.container.get('except','')
        if (nested==current and tries==""):
            self.container['context'] = ""
            self.container['current'] = f"{anterior}"
        self.container['nested'] = f"{anterior}"
        self.debug(f'visit_If finish: {node}, container: {self.container}')
        self.usage = Usage.make(0, '')
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.debug(f'visit_ExceptHandler: begin: {node}')
        self.debug(f'visit_ExceptHandler: container: {self.container}')
        # self.container['context'] = "" #por agora, não queremos as apis que ocorrem no except
        nested = self.container.get('nested','')
        current = self.container.get('current','')
        if (nested==current):
            self.container['context'] = ""
        self.generic_visit(node)
        self.debug(f'visit_ExceptHandler finish: {node}')
            
    def capture_bool(self, node):
        # self.usage = Usage.make(0, '')
        self.debug(f"capture_bool:begin: line: {self.usage.line}, API: {self.usage.api}, platforms: {self.usage.platforms}, node: {node}")      
        if isinstance(node, ast.Compare):
            self.capture_compare(node)
        if isinstance(node, ast.Call):
            self.capture_call(node)
            
        if isinstance(node, ast.UnaryOp):
            self.debug(f'ast.UnaryOp -- {node}, op: {node.op}')
            self.capture_bool(node.operand)
        if isinstance(node, ast.BoolOp):
            self.debug(f'capture_bool:ast.BoolOp -- {node}')
            for value in node.values:
                self.debug(f'capture_bool:ast.BoolOp:value -- {value}')
                self.capture_bool(value)
        if(isinstance(node, ast.Attribute)):
            self.usage.line = node.lineno
            self.usage.api = self.xyz(node)
                
        self.debug(f"capture_bool:apis: line: {self.usage.line}, API: {self.usage.api}, platforms: {self.usage.platforms}")      
        if self.is_os_api():
            self.usages.add(self.usage)
            context = self.container.get('context','')
            conditional = self.container.get('conditional','')
            decorator = self.container.get('decorator','')
            self.debug(f"capture_bool:add_usages:begin {self.container}")  
            self.container['current'] = self.container.get('nested','') #caputar o statement atual
            if(context!="yes" and (conditional !="" or decorator!="")):
                self.container['context'] = "yes"
                # self.container['current'] = self.container.get('nested','')
                self.debug(f"capture_bool:add_usages: {self.container}")     
                 
        self.usage = Usage.make(0,'') 
            
        self.debug(f"capture_bool:end: line: {self.usage.line}, API: {self.usage.api}, platforms: {self.usage.platforms}")      
        # self.usage = Usage.make(0,'') 
    
    def is_os_api(self):
        os_apis = ['sys.platform', 'sys.getwindowsversion', 'os.name', 'os.supports_bytes_environ', 'os.uname',
                'platform.platform', 'platform.system', 'platform.version', 'platform.uname', 'platform.win32_edition',
                'platform.win32_ver', 'platform.win32_is_iot', 'platform.mac_ver', 'platform.libc_ver', 'platform.freedesktop_os_release']
        for api in os_apis:
            if api == self.usage.api:
                 return True
        return False 
        
    def capture_compare(self, compare:ast.Compare):
        # print('capture_compare: ',compare)
        self.debug(f'capture_compare:left: {compare.left}')
        self.debug(f'capture_compare:comparators: {compare.comparators}')
        # api = ''
        # line = 0
        # self.usage = Usage.make(0, '')
        # platforms = set()         
        
        if(isinstance(compare.left, ast.Tuple) or isinstance(compare.left, ast.List)):
            for tuple in compare.left.elts:
                self.capture_bool(tuple)
        if(isinstance(compare.left, ast.Subscript)):
            self.debug(f'capture_compare:ast.subscript: {compare.left.slice} value: {compare.left.value}')
            if(isinstance(compare.left.value, ast.Attribute)):
                self.usage.line = compare.lineno
                self.usage.api = self.xyz(compare.left.value)
                
                for comparator in compare.comparators:  
                    if isinstance(comparator, ast.Constant):
                        # print('capture_compare: comparator: ',comparator.value)
                        self.usage.platforms.add(comparator.value)
                    if isinstance(comparator, ast.Tuple) or isinstance(comparator, ast.List):
                        for elts in comparator.elts:  
                            # print('capture_compare: elts-tuple:',elts.value)
                            if isinstance(elts, ast.Constant):
                                self.usage.platforms.add(elts.value)
                            if isinstance(elts, ast.Name):
                                self.usage.platforms.add(elts.id)  
            if(isinstance(compare.left.value, ast.Call)):                   
                self.capture_bool(compare.left.value)    
        if(isinstance(compare.left, ast.Attribute)):
          self.debug(f"capture_compare: line: {compare.lineno} , API: {self.flatten_attr(compare.left)}, xyz: {self.xyz(compare.left)}")  
        #   api = self.flatten_attr(compare.left)
        #   line = compare.lineno
        #   api = self.xyz(compare.left)
          self.usage.line = compare.lineno
          self.usage.api = self.xyz(compare.left)
          
          for comparator in compare.comparators:  
            if isinstance(comparator, ast.Constant):
                # print('capture_compare: comparator: ',comparator.value)
                self.usage.platforms.add(comparator.value)
            if isinstance(comparator, ast.Tuple) or isinstance(comparator, ast.List):
                for elts in comparator.elts:  
                    # print('capture_compare: elts-tuple:',elts.value)
                    if isinstance(elts, ast.Constant):
                        self.usage.platforms.add(elts.value)
                    if isinstance(elts, ast.Name):
                        self.usage.platforms.add(elts.id)      
        if(isinstance(compare.left, ast.Constant)):
            self.usage.platforms.add(compare.left.value)
            for comparator in compare.comparators:  
                if isinstance(comparator, ast.Attribute):
                    self.usage.line = comparator.lineno
                    self.usage.api = self.xyz(comparator)
        if(isinstance(compare.left, ast.Call)):
            self.debug(f"capture_compare:call: arguments: {compare.left.args}, keywords: {compare.left.keywords}, func: {compare.left.func}")  
            if(isinstance(compare.left.func, ast.Attribute)):
                self.usage.line = compare.lineno
                self.usage.api = self.xyz(compare.left.func)
            self.capture_call(compare.left)
            # self.capture_bool(compare.left)
            
            
            # platform.system() == 'Linux' # conseguimos capturar a plataforma por meio do compare, não do argumento da função
            if(compare.left.args is None or compare.left.args == [] ):
                for comparator in compare.comparators:  
                    if isinstance(comparator, ast.Constant):
                        self.usage.platforms.add(comparator.value)
                    if isinstance(comparator, ast.Tuple) or isinstance(comparator, ast.List):
                        for elts in comparator.elts:  
                            if isinstance(elts, ast.Constant):
                                self.usage.platforms.add(elts.value)
                            if isinstance(elts, ast.Call):
                                self.capture_call(elts)
        
        for comparator in compare.comparators: # capturar o lado direito do compare
            self.debug(f'capture_compare:right: {comparator}')
            if(isinstance(comparator, ast.Attribute)):
                self.debug(f'capture_compare:right:attr: {comparator}')
                self.usage.line = compare.lineno
                self.usage.api = self.xyz(comparator)
                self.capture_bool(comparator)
            if isinstance(comparator, ast.Call): #if 'windows' in platform.platform().lower():
                self.capture_bool(comparator)
                # for arg in comparator.args:
                #     self.capture_bool(arg)
                # self.capture_call(comparator)
            if isinstance(comparator, ast.Constant):
                    # print('capture_compare: comparator: ',comparator.value)
                    self.usage.platforms.add(comparator.value)
            if isinstance(comparator, ast.Tuple) or isinstance(comparator, ast.List):
                for elts in comparator.elts:  
                    # print('capture_compare: elts-tuple:',elts.value)
                    if isinstance(elts, ast.Constant):
                        self.usage.platforms.add(elts.value)
                    if isinstance(elts, ast.Name):
                        self.usage.platforms.add(elts.id)    
            if isinstance(comparator, ast.JoinedStr):
                self.debug(f'capture_compare:JoinedStr: {comparator.values}')
                for value in comparator.values: #capture_compare:JoinedStr: [<ast.Constant object at 0x104940a90>, <ast.FormattedValue object at 0x104940a60>]
                    if isinstance(value, ast.Constant):
                        self.debug(f'capture_compare:JoinedStr:value: {value.value}')
                        self.usage.platforms.add(value.value)
                    if isinstance(value, ast.FormattedValue):
                        self.debug(f'capture_compare:JoinedStr:FormattedValue: {value.value}')
                        self.capture_bool(value.value)
                    # self.usage.platforms.add(comparator.value)     
            # self.capture_bool(comparator)
            
        self.debug(f"capture_compare: end: line: {self.usage.line}, API: {self.usage.api}, platforms: {self.usage.platforms}")  

            # if isinstance(comparator, ast.List):
            #     self.compare_temp = comparator.elts    
            #     for elts in comparator.elts:  
            #         print('capture_compare: elts-list:',elts.value)

    def xyz(self, attribute:ast.Attribute):
        if isinstance(attribute.value, ast.Attribute):
            return self.xyz(attribute.value)
        if isinstance(attribute.value, ast.Name):
            # return str(self.flatten_attr(node.value)) + '.' + node.attr
            return attribute.value.id + "." +attribute.attr
            # if attribute.value.id in self.chamadas:
            #     self.razion['module'] = self.chamadas[attribute.value.id][0]
            # else:                 
            #     self.razion['module'] = attribute.value.id
    
    # Call(expr func, expr* args, keyword* keywords)                
    def capture_call(self, call:ast.Call):
        if(not isinstance(call, ast.Call)):
            return 
        self.debug(f'capture_call: {call.args}, func: {call.func}')
        # api = ''
        # line = 0
        # platforms = set()         
        if(isinstance(call.func, ast.Name)): # uma chamada como argumento: any(platform.win32_ver())
            self.debug(f'capture_call:name: {call.func.id}')
            self.debug(f'capture_call:args: {call.args}')
            for comparator in call.args:  
                self.debug(f'comparator:name: {comparator}')
                if isinstance(comparator, ast.Call):
                    self.capture_call(comparator)
                if isinstance(comparator, ast.Constant):
                    # print('capture_compare: comparator: ',comparator.value)
                    self.usage.platforms.add(comparator.value)
                if isinstance(comparator, ast.Tuple) or isinstance(comparator, ast.List):
                    for elts in comparator.elts:  
                        # print('capture_compare: elts-tuple:',elts.value)
                        if isinstance(elts, ast.Constant):
                            self.usage.platforms.add(elts.value)
                        if isinstance(elts, ast.Name):
                            self.usage.platforms.add(elts.id)
            # capturar o hasattr
            if (call.func.id =="hasattr") :
                if isinstance(call.args[1], ast.Constant): #TODO: apenas valores constantes no segundo parametro
                    if isinstance(call.args[0], ast.Name): #TODO: excluindo chamadas a self.hasattr 
                        api = f"{call.args[0].id}.{call.args[1].value}"
                        self.debug(f'capture_call:hasattr: api:  {api}, args: {call.args}') #module_name = call.args[0] #api_name = call.args[1]
                        
                        if  self.is_call_from_module(call.args[1].value, call.args[0]): 
                            
                            call_name = call.args[1].value
                            module_name = self.chamadas[call.args[0].id][0]
                            if call_name == "":
                                call_name = call.args[0].id
                            
                            # call_name_long = ""    
                            if not module_name in self.libs_os: #and module_name in self.chamadas:
                                # call_name_long = f"{module_name}.{call_name}" # para capturar com dot
                                module_name = self.chamadas[module_name][0]
                            
                            api = f"{module_name}.{call_name}"
                            if self.is_member_of(module_name, call_name):
                                self.debug(f'capture_call:hasattr: api {api}, container: {self.container}') #module_name = call.args[0] #api_name = call.args[1]
                                context = self.container.get('context','')
                                if(context!="yes"):
                                    self.container['context'] = "yes"
                                    self.container['current'] = self.container.get('nested','')
                                # if api in self.libs_os: #and module_name in self.chamadas:
                                #     # module_name = self.chamadas[module_name][0]
                                #     # if  self.is_member_of(module_name, call_name):
                                #     self.debug(f'capture_call:hasattr: api:{api} ') #module_name = call.args[0] #api_name = call.args[1]
                
        if(isinstance(call.func, ast.Attribute)):
        #   print(f"capture_call: line: {line} , API: {call.func.value.value.id}")  
          
        #   line = call.lineno
        #   api = self.xyz(call.func)
          
          self.usage.line = call.lineno
          self.usage.api = self.xyz(call.func)
          self.debug(f'capture_call:flatten: {self.flatten_attr(call.func)}, xyz: {self.xyz(call.func)}, attribute: {call.func.attr}, attribute-value: {call.func.value}')
          if(isinstance(call.func.value, ast.Call)): # platform.system().lower() 
                self.capture_bool(call.func.value)
        #   self.debug(f'parents: {self.get_parent(call.func)}')
          self.debug(f'capture_call:args: {self.usage.api}')
          for comparator in call.args:  
            self.debug(f'comparator: {comparator}')
            if isinstance(comparator, ast.Call):
                self.capture_call(comparator)
            if isinstance(comparator, ast.Constant):
                # print('capture_compare: comparator: ',comparator.value)
                self.usage.platforms.add(comparator.value)
            if isinstance(comparator, ast.Tuple) or isinstance(comparator, ast.List):
                for elts in comparator.elts:  
                    # print('capture_compare: elts-tuple:',elts.value)
                    if isinstance(elts, ast.Call): #
                        self.capture_call(comparator)
                    if isinstance(elts, ast.Constant):
                        self.usage.platforms.add(elts.value)
         
        for arg in call.args:
            self.debug(f'comparator:args: {arg}')   
            self.capture_bool(arg)   
        
        for arg in call.keywords:
            self.debug(f'comparator:keywords: {arg.value}')
            self.capture_bool(arg.value)   
        # if(isinstance(compare.left, ast.Constant)):
        #     platforms.add(compare.left.value)
        #     for comparator in compare.comparators:  
        #         if isinstance(comparator, ast.Attribute):
        #             line = comparator.lineno
        #             api = self.flatten_attr(comparator)
            
        self.debug(f"capture_call: end: line: {self.usage.line}, API: {self.usage.api}, platforms: {self.usage.platforms}")  
        
    def visit_Try(self, node: ast.Try):
        # self.p = node
        self.debug(f'visit_Try begin: {node}')
        # self.debug(f'excepts: {node.handlers}')
        excepthandler = self.container.get('excepthandler',set())
        for h in node.handlers:
            if isinstance(h.type, ast.Name):
                self.debug(f'excepts: name: {h.type.id}')
                excepthandler.add(h.type.id)
            elif isinstance(h.type, ast.Tuple):
                for l in h.type.elts:
                    if (isinstance(l, ast.Attribute)):
                        self.debug(f'excepts: tuple: attribute {l.value}')    
                        excepthandler.add(l.value)
                    else:    
                        self.debug(f'excepts: tuple: {l.id}')
                        excepthandler.add(l.id)
            # self.debug(f'excepts: name: {h.type}')
        # anterior = self.container.get('except','')
        anterior = self.container.get('nested','')
        self.container['excepthandler'] = excepthandler
        self.container['except'] = f"/try"
        self.container['nested'] = f"{anterior}/try"
        # self.container['context'] = "yes"
        context = self.container.get('context','')
        if(context!="yes"):
            self.container['context'] = "yes"
            self.container['current'] = self.container.get('nested','')
        self.generic_visit(node)
        # self.p = None
        self.container['except'] = f""
        self.debug(f'visit_Try:container: {self.container}')
        nested = self.container.get('nested','')
        current = self.container.get('current','')
        if (nested==current):
            self.container['context'] = ""
        
        self.container['nested'] = f"{anterior}"
        self.container['excepthandler'] = set()
        self.debug(f'visit_Try finish: {node}')
    
    def flatten_attr(self, node):
        if isinstance(node, ast.Attribute):
            return str(self.flatten_attr(node.value)) + '.' + node.attr
        elif isinstance(node, ast.Name):
            return str(node.id)
        else:
            pass
    def parse_decorator(self, node):
        self.debug(f'parse_decorator:begin: {node}')    
        for d in node.decorator_list:
            self.debug(f'parse_decorator:internal: {d}')    
            decorator = ''
            if isinstance(d, ast.Call):
                # self.container['decorator']  = self.flatten_attr(d.func)
                decorator  = self.flatten_attr(d.func)
            if isinstance(d, ast.Attribute):
                # self.container['decorator'] = self.flatten_attr(d) #TODO: não estou removendo, o decorator pode fazer parte de outras funções
                decorator = self.flatten_attr(d) #TODO: não estou removendo, o decorator pode fazer parte de outras funções
            
            if not decorator in self.decorators:
                continue

            self.container['decorator'] = decorator    
            self.capture_bool(d)
            if not isinstance(d, ast.Call):
                continue
            for arg in d.args:  
                self.debug(f'parse_decorator:internal:args: {arg}')    
                self.capture_bool(arg)  
                
        self.debug(f"parse_decorator:end: {self.container}")
        ant = self.container.get('class','')
        
        self.container['decorator'] = ""    
        # for d in node.decorator_list:
        #     if not isinstance(d, ast.Call):
        #         continue
        #     decoratorAtt = self.flatten_attr(d.func)
        #     if not decoratorAtt in self.decorator:
        #         continue
        #     self.razion = dict()
        #     self.razion['decorator'] = decoratorAtt
        #     for a in d.keywords:
        #         if isinstance(a.value, ast.Constant):
        #             if 'reason' == a.arg:
        #                 self.razion['razion'] = a.value.value
        #                 self.razion['line'] = a.value.lineno
        #                 self.razion['url'] = self.gerar_url(a.value.lineno)
                
                  
            # if isinstance(d, ast.Call):
            #     continue
            # decoratorAtt = self.flatten_attr(d.func)
           
               
def all_files(dir, extension='.py'):
    """ 
    List all files in dir
    """
    from pathlib import Path
    path = Path(dir)
    files = []
    for file in path.rglob(pattern=f'*{extension}'):
        files.append(file)
    return files

def read_apis():
    import json
    with open('psae/apis-os.json', 'r') as file:
        data = json.load(file)
    return data
    # import json
    # file = open('psae/apis-os.json')
    # return json.load(file)

def local():
    # https://raw.githubusercontent.com/sanic-org/sanic/a5a9658896984ddad484e168d4cb5c96e589fbad/tests/test_multiprocessing.py
    # https://github.com/celery/celery/blob/fe762c3a26e56ff34608244fc04336b438f8fa0c/celery/platforms.py#L542
    # project_dir = "/Users/job/Documents/dev/doutorado/study/study-docs/input/classes"
    # project_dir = "tests/classes/handle"
    project_dir = "tests/classes/on"
    os_apis = read_apis()
    for python_file in all_files(project_dir):
        if python_file.is_dir(): continue
        filename = str(python_file).replace(project_dir,"")
        try:
            file_compile = ast.parse(open(python_file).read())
            checkVisitor = CheckVisitor(os_apis)
            checkVisitor.debug(f"parse from: {python_file}")
            checkVisitor.visit(file_compile)
            [print(f'{c.line}; {c.api}; {c.platforms}') for c in checkVisitor.usages]
            [print(f'name; hash; {c.line}; {c.module}; {c.call_name}; {c.call_name_long}; {filename}') for c in checkVisitor.calls]
        except SyntaxError as ex:
            print('erro', python_file) 

def github():
    import requests
    os_apis = read_apis()
    # python_file = 'https://raw.githubusercontent.com/ytdl-org/youtube-dl/213d1d91bfc4a00fefc72fa2730555d51060b42d/test/test_utils.py'
    # python_file = 'https://raw.githubusercontent.com/django/django/2eb1f37260f0e0b71ef3a77eb5522d2bb68d6489/tests/asgi/tests.py'
    # python_file = 'https://raw.githubusercontent.com/django/django/2eb1f37260f0e0b71ef3a77eb5522d2bb68d6489/tests/i18n/test_extraction.py#L70'
    python_file = 'https://raw.githubusercontent.com/ansible/ansible/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107'
    # https://github.com/ansible/ansible/blob/a84b3a4e7277084466e43236fa78fc99592c641a/test/support/integration/plugins/modules/timezone.py#L107
    try:
        filename = "github"
        f = requests.get(python_file)
        # print(f.content)
        file_compile = ast.parse(f.content)
        checkVisitor = CheckVisitor(os_apis)
        checkVisitor.visit(file_compile)
        [print(f'{c.line}; {c.api}; {c.platforms}') for c in checkVisitor.usages]
        [print(f'name; hash; {c.line}; {c.module}; {c.call_name}; {c.call_name_long}; {filename}') for c in checkVisitor.calls]
    except SyntaxError as ex:
        print('erro', ex) 
if __name__ == '__main__':
    # local()
    github()
 
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
           