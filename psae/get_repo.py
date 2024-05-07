# import pydriller
import os
from pydriller import Repository
from pydriller import Git


class Local:
    def __init__(self, dir):
        self.dir_local = dir
    
    def commit_head(self)-> str:
        gr = Git(self.dir_local)
        return gr.get_head().hash
    
    def path(self):
        return self.dir_local
        
class Repo:
    def __init__(self, url):
        self.url = url

    def clone_at(self, dir) -> Local:
        dir_repo = dir 
        repo = Repository(self.url,  clone_repo_to=dir)
        if not os.path.exists(dir):
            dir_repo = repo._clone_remote_repo(repo=self.url, tmp_folder=dir)
        local = Local(dir_repo)
        return local
    
    def repo_name(self):
        return self.url.replace("https://github.com/", "")