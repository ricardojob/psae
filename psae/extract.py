import os
import os.path
class ExtractPlatformSpecific:
    def __init__(self, content):
        self.content = content   
        
    def touch(self):
        print(self.content)
    
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
        print(content, self.output)
        # utils.write_csv(
        #     entries,
        #     sys.stdout,
        #     entries[0].__class__,
        #     not no_headers,
        #     repository_name,
        # )