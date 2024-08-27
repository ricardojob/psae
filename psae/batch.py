import ast
import csv
import os.path
import logging
import shutil
import datetime
from typing import List
import click

from projects import Project, ProjectRemote
from psae.capture import CheckVisitor, Usage, Call

logging.basicConfig(level=logging.INFO, filename='log.txt')
logger = logging.getLogger(__name__)

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--output-directory",
    "-o",
    help="The directory where the usage of Platform-Specific APIs related to the repository will be stored.",
    default = "data",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
    
)
@click.option(
    "--from",
    "from_",
    help="The TXT file with the list of projects to be extracted. "
    "In the file, the content of each line must follow the pattern <owner>/<repo>.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False),
)
@click.option(
    '--platforms',
    '-p',
    help="The Platform-specific API group to figure out.", 
    type=click.Choice(['all', 'OS'], case_sensitive=True), is_flag=False, flag_value="Flag", default="all"
)
@click.option(
    "--filter",
    "-f",
    help="The JSON file with the configuration of Platform-Specific APIs that will be filter. "
    "By default, this option is mandatory to option --platforms.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False),
)
def batch(
    output_directory, 
    from_,
    platforms,
    filter
):
    """Extract the usage of Platform-Specific APIs from a single Git repository `REPOSITORY`.
    The Git repository can be local or remote. In the latter case, it will be pulled
    locally in the folder `data`.
    Every extracted Platform-Specific APIs will be written in the CSV file given to `-o`,
    or in the standard output if not specified.

    Example of usage:
    python psae/batch.py --from projects.txt -o output
    """
    load_apis = ''
    if(filter):
        load_apis = filter
    else:
        if(platforms):
            if platforms == 'all':
                    load_apis = 'psae/apis-all.json'
            if platforms == 'OS':
                    load_apis = 'psae/apis-os.json'
    logger.debug(f'load: {load_apis}')
    calls_headear =   ['project_name','project_hash', 'line', 'module', 'call', 'is_test' ,'filename', 'url', 'risk']
    # usages_headear =  ['project_name','project_hash', 'line', 'api', 'platforms', 'is_test' ,'filename', 'url']
    usages_headear =  ['project_name','project_hash', 'line', 'api',  'is_test' ,'filename', 'url']
    metadata_header = ['project_name', 'project_hash',  'project_files', 'apis_use',
                        'tests_files', 'tests_files_api_use', 'apis_use_in_tests_files',
                        'prod_files', 'prod_files_api_use', 'apis_use_in_prod_files',
                        "count_tests_files_usages", "count_usages_in_tests_files", "count_prod_files_usages", 
                        "count_usages_in_prod_files", "count_usages"]
    
    def __map_to_call(filename, c):
        c.filename = filename # _replace(filename=filename) 
        c.is_test = 'test' in filename # verify filename
        c.project_name = project.project_name
        c.project_hash = project.project_hash
        c.url = __build_url(c)
        
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
        call.append(c.risk)
        return call
    
    def __map_to_usage(filename, usage):
        url = __build_from(project.project_name,project.project_hash, filename, usage.line)
        usage_row = []
        usage_row.append(project.project_name)
        usage_row.append(project.project_hash)
        usage_row.append(usage.line)
        usage_row.append(usage.api)
        # usage_row.append(",".join(usage.platforms))
        usage_row.append('test' in filename)  # verify filename
        usage_row.append(filename)
        usage_row.append(url)
        return usage_row
        
    def __build_url(c:Call):
        # return f'https://github.com/{c.project_name}/blob/{c.project_hash}{c.filename}#L{c.line}'  
        return __build_from(c.project_name, c.project_hash, c.filename, c.line)
    
    def __build_from(name, hash, filename, line):
        return f'https://github.com/{name}/blob/{hash}{filename}#L{line}'  
    
    def __all_files(dir, extension='.py'):
        """ List all files in dir. """
        from pathlib import Path
        path = Path(dir)
        files = []
        for file in path.rglob(pattern=f'*{extension}'):
            files.append(file)
        logging.info(msg = f" A total of {len(files)} python files were computed.")
        return files   
    
    class ExtractAllSpecific: #may be update
        def __init__(self, os_apis):
            self.os_apis = os_apis   
            self.declared_api = False
            
        def touch(self, content):
            file_compile = ast.parse(content)
            checkVisitor = CheckVisitor(self.os_apis)
            checkVisitor.visit(file_compile)
            apis = checkVisitor.calls
            usages = checkVisitor.usages
            self.declared_api = checkVisitor.is_declared_apis()
            logging.debug(msg = f" A total of {len(apis)} platform-specific apis were computed.")
            logging.debug(msg = f" A total of {len(usages)} usages apis were computed.")
            return apis, usages
    
    class ReportToCSV():
        def __init__(self, output, header):
            self.output = output
            self.header = header
            # self.call_headear = ['project_name','project_commit', 'line', 'module', 'call', 'is_test' ,'filename', 'url', 'risk']
        
        def write(self, content):
            parent = os.path.dirname(self.output)
            if parent != "":
                os.makedirs(parent, exist_ok=True)
            with open(self.output, 'w', encoding="utf-8") as file:
                write = csv.writer(file, delimiter =";")
                write.writerow(self.header)
                write.writerows(content)
    
    with open(from_, 'r', encoding='utf-8') as file:
        projects = file.readlines()
         
        for project_name in projects:
            # print(project_name.strip())
            start_time = datetime.datetime.now()     
            count_apis_use = 0 # number of os-apis in project
            count_project_files = 0 # number of project files processed
            count_tests_files = 0 # number of tests files 
            count_tests_files_apis_use = 0 # number of tests files that use the os-apis 
            count_apis_use_in_tests_files = 0 # number of os-apis in tests files
            
            count_prod_files = 0 # number of prod files 
            count_prod_files_apis_use = 0 # number of prod files that use the os-apis 
            count_apis_use_in_prod_files = 0 # number of os-apis in prod files
            
            #sys.platform usages
            count_tests_files_usages = 0 # number of tests files that use the os-identify 
            count_usages_in_tests_files = 0 # number of os-identify in tests files
            count_prod_files_usages = 0 # number of prod files that use the os-identify
            count_usages_in_prod_files = 0 # number of os-identify in prod files
            count_usages = 0
            
            project =  ProjectRemote(load_apis, directory=output_directory).clone(project_name.strip())
            
            calls_apis = []
            usages_apis = []
            metadata = []
                
            for python_file in __all_files(project.directory):
                try:
                    if python_file.is_dir(): continue
                    filename = str(python_file).replace(project.directory,"")
                    logging.debug(msg = f" Parse from: {str(python_file)}, filename: {str(filename)}")
                    content = open(python_file, 'rb').read().decode(errors='ignore')
                    extract  = ExtractAllSpecific(project.read_apis())
                    apis, usages = extract.touch(content)
                    
                    count_project_files = count_project_files + 1
                    if 'test' in filename: 
                        count_tests_files = count_tests_files + 1
                    else:
                        count_prod_files = count_prod_files + 1
                    if not extract:  continue 
                    
                    for c in apis:
                        calls_apis.append(__map_to_call(filename, c))
                    for usage in usages:
                        usages_apis.append(__map_to_usage(filename, usage))
                    
                    length = len(calls_apis)    
                    if length > 0:
                        if 'test' in filename: 
                            count_tests_files_apis_use = count_tests_files_apis_use + 1
                            count_apis_use_in_tests_files = count_apis_use_in_tests_files + length
                        else:
                            count_prod_files_apis_use = count_prod_files_apis_use + 1
                            count_apis_use_in_prod_files = count_apis_use_in_prod_files + length  
                    
                    length = len(usages)    
                    if length > 0:
                        if 'test' in filename: 
                            count_tests_files_usages = count_tests_files_usages + 1
                            count_usages_in_tests_files = count_usages_in_tests_files + length
                        else:
                            count_prod_files_usages = count_prod_files_usages + 1
                            count_usages_in_prod_files = count_usages_in_prod_files + length  
                except SyntaxError as ex:
                    logger.error(
                        "Could not process python (file=%s)",
                        str(python_file),
                        exc_info=True,
                    )
                except (FileNotFoundError, UnicodeDecodeError,  Exception, BaseException, TypeError) as ex:
                    logger.error(
                        f'Error: {ex} in (file=%s)',
                        str(python_file),
                        exc_info=True,
                    )
                
                count_apis_use = count_apis_use_in_tests_files +  count_apis_use_in_prod_files
                count_usages = count_usages_in_tests_files +  count_usages_in_prod_files
                
            row = [project.project_name, project.project_hash, count_project_files, 
                    count_apis_use, count_tests_files,  count_tests_files_apis_use,  
                    count_apis_use_in_tests_files, count_prod_files,  count_prod_files_apis_use,
                    count_apis_use_in_prod_files, count_tests_files_usages, count_usages_in_tests_files, 
                    count_prod_files_usages, count_usages_in_prod_files, count_usages]
                    
            metadata.append(row)

            os.makedirs("reports", exist_ok=True)
            sufix = f'reports/%s/{project_name.strip().replace("/","_")}.csv'
            ReportToCSV(sufix % "calls", calls_headear).write(calls_apis)
            ReportToCSV(sufix % "usages", usages_headear).write(usages_apis)
            ReportToCSV(sufix % "metadata", metadata_header).write(metadata)
            
            time_elapsed = datetime.datetime.now() - start_time     
            logger.info(f"{project_name.strip()}, {'Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed)}")
                # writer = WriterCSV(name=f'experiment_{project_name.replace("/","_")}_call', path=f"{experiment_dir}/experiment")
                # writer.write(head=call_headear, rows=calls)

                # call_all.extend(calls) 
                    # raise
                # print('Calls from: ', filename)    
                # [print(c) for c in calls_apis]
                # print('Usages from: ', filename)
                # [print(u) for u in usages_apis]
            
            # shutil.rmtree(project.directory)
            shutil.rmtree(output_directory)

if __name__ == "__main__":
    batch()

# class ExtractAllSpecificRepo:
#     def __init__(self, project):
#         self.project = project
#         self.directory = project.directory
#         self.calls_apis = []  
#         self.os_apis = project.read_apis()
        
#     def touch(self) -> List[Call]: 
#         # project_dir = "/Users/job/Documents/dev/doutorado/study/study-docs/input/classes"
#         for python_file in self.__all_files(self.directory):
#             try:
#                 if python_file.is_dir(): continue
#                 filename = str(python_file).replace(self.directory,"")
#                 logging.info(msg = f" Parse from: {str(python_file)}, filename: {str(filename)}")
#                 content = open(python_file).read()
#                 extract  = ExtractAllSpecific(self.os_apis)
#                 apis = extract.touch(content)
#                 for c in apis:
#                     self.calls_apis.append(self.__map_to_call(filename, c))
#             except SyntaxError as ex:
#                 logger.error(
#                     "Could not process python (file=%s)",
#                     str(python_file),
#                     exc_info=True,
#                 )
#                 # raise
#         return self.calls_apis

#     def __map_to_call(self, filename, c):
#         c.filename = filename # _replace(filename=filename) 
#         c.is_test = 'test' in filename # verify filename
#         c.project_name = self.project.project_name
#         c.project_hash = self.project.project_hash
#         c.url = self.__build_url(c)
        
#         call = []
#         call.append(c.project_name)
#         call.append(c.project_hash)
#         call.append(c.line)
#         call.append(c.module)
#         call.append(c.call_name)
#         # call.append(c.call_name_long)
#         call.append(c.is_test) # verify filename
#         call.append(c.filename)
#         call.append(c.url)
#         return call
        
#     def __build_url(self, c:Call):
#         return f'https://github.com/{c.project_name}/blob/{c.project_hash}{c.filename}#L{c.line}'  
    
#     def __all_files(self, dir, extension='.py'):
#         """ List all files in dir. """
#         from pathlib import Path
#         path = Path(dir)
#         files = []
#         for file in path.rglob(pattern=f'*{extension}'):
#             files.append(file)
#         logging.info(msg = f" A total of {len(files)} python files were computed.")
#         return files   
        
