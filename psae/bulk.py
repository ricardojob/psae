import ast
import shutil
from capture import CheckVisitor
from get_repo import Repo
from writercsv import WriterCSV
import csv

def clone(repo_name):
    dir = f'data/{repo_name}'
    url = f'https://github.com/{repo_name}'
    repo = Repo(repo_name,url)
    local = repo.clone_at(dir)
    print(f'clone: {repo.name}')
    commit_hash = local.commit_head()
    return repo.name, commit_hash, local.path()

def build_url(project_name, project_hash, filename, line):
    return f'https://github.com/{project_name}/blob/{project_hash}{filename}#L{line}'  

def all_files(dir, extension='.py'):
    from pathlib import Path
    path = Path(dir)
    files = []
    for file in path.rglob(pattern=f'*{extension}'):
        files.append(file)
    return files

def read_apis():
    import json
    file = open('experiment/apis-os.json')
    return json.load(file)

if __name__ == '__main__':
    experiment_dir = "analysis/round-05"
    experiment_filename = 'input-csv/projects_filted_dev.csv'
    has_head_readed = False
    os_apis =  read_apis()
    call_headear = ['project_name','project_hash', 'line', 'module', 'call', 'is_test' ,'filename', 'url', 'risk']
    metadata_header = ['project_name', 'project_hash',  'project_files', 'apis_use',
                              'tests_files', 'tests_files_api_use', 'apis_use_in_tests_files',
                              'prod_files', 'prod_files_api_use', 'apis_use_in_prod_files']
    call_all = []
    metadata = []
    
    with open(experiment_filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if not has_head_readed: #skip head
                has_head_readed = True
                continue  
            
            count_apis_use = 0 # number of os-apis in project
            count_project_files = 0 # number of project files processed
            count_tests_files = 0 # number of tests files 
            count_tests_files_apis_use = 0 # number of tests files that use the os-apis 
            count_apis_use_in_tests_files = 0 # number of os-apis in tests files
            
            count_prod_files = 0 # number of prod files 
            count_prod_files_apis_use = 0 # number of prod files that use the os-apis 
            count_apis_use_in_prod_files = 0 # number of os-apis in prod files
            
            project_name, project_hash, project_dir = clone(row[0])
            # project_name, project_hash, project_dir = dev()
            calls = []
            
            for python_file in all_files(project_dir):
                if python_file.is_dir(): continue #only files
                filename = str(python_file).replace(project_dir,"") # if not 'test' in filename: continue #only test files
                try:
                    parser = ast.parse(open(python_file, 'rb').read())
                    file_compile = ast.parse(open(python_file).read())
                    checkVisitor = CheckVisitor(os_apis)
                    checkVisitor.debug(f"parse from: {python_file}")
                    checkVisitor.visit(file_compile)
                    count_project_files = count_project_files + 1
                    if 'test' in filename: 
                        count_tests_files = count_tests_files + 1
                    else:
                        count_prod_files = count_prod_files + 1
                    if not checkVisitor.modules:  continue 
                    if not set(os_apis.keys()).intersection(checkVisitor.modules): continue
                    
                    if checkVisitor.calls is not None:
                        for c in checkVisitor.calls:
                            call = []
                            call.append(project_name)
                            call.append(project_hash)
                            call.append(c.line)
                            call.append(c.module)
                            call.append(c.call_name)
                            # call.append(c.call_name_long)
                            call.append('test' in filename) # verify filename
                            call.append(filename)
                            call.append(build_url(project_name, project_hash, filename, c.line))
                            calls.append(call)
                            
                        length = len(checkVisitor.calls)    
                        if length > 0:
                            if 'test' in filename: 
                                count_tests_files_apis_use = count_tests_files_apis_use + 1
                                count_apis_use_in_tests_files = count_apis_use_in_tests_files + length
                            else:
                                count_prod_files_apis_use = count_prod_files_apis_use + 1
                                count_apis_use_in_prod_files = count_apis_use_in_prod_files + length    
                except SyntaxError as ex:
                    print(f'SyntaxError: {ex} in {python_file}') 
                except FileNotFoundError as ex:
                    print(f'FileNotFoundError: {ex} in {python_file}') 
                except UnicodeDecodeError as ex:
                    print(f'UnicodeDecodeError: {ex} in {python_file}') 
            
            count_apis_use = count_apis_use_in_tests_files +  count_apis_use_in_prod_files
            
            metadata.append(
                [project_name, project_hash,count_project_files, count_apis_use,
                 count_tests_files,  count_tests_files_apis_use,  count_apis_use_in_tests_files,
                 count_prod_files,  count_prod_files_apis_use, count_apis_use_in_prod_files])
            
            writer = WriterCSV(name=f'experiment_{project_name.replace("/","_")}_call', path=f"{experiment_dir}/experiment")
            writer.write(head=call_headear, rows=calls)

            call_all.extend(calls) 
            shutil.rmtree(project_dir)
            print(f'finish: {project_name}')                 
        
    writer = WriterCSV(name=f'experiment_all_call', path=experiment_dir)
    writer.write(head=call_headear, rows=call_all)
    
    writer = WriterCSV(name=f'experiment_metadata', path=experiment_dir)
    writer.write(head=metadata_header, rows=metadata)