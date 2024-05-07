import asyncio 
from asyncio import Task 
# Task.cancel
def asyncio_server():    
    z = Task() #call
    z.wait() 
    s = asyncio.Task() #call
    s.dones() 
    # s.close() 

# import asyncio
# from asyncio import Server 
# def asyncio_server():    
#     name = Server() #call
#     name.close()
#     s = asyncio.Server() #call
#     s.close()
# https://medium.com/@pgjones/an-asyncio-socket-tutorial-5e6f3308b8b0
# def main(host, port):
#     loop = asyncio.get_running_loop() #call
#     server = loop.create_server(None, host, port)
#     server.serve_forever()    
# asyncio_server() 
# class ClassName:
#     def __init__(self,name):
#         self.name = name
#     def print(self):
#         print(f"class name: {self.name}")
        
# def class_name():
#     c =  ClassName('Job')
#     c.print()