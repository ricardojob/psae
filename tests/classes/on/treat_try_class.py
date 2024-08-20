import os 
import sys 

def asyncio_server():    
    # if sys.platform != "win32":
    try:
        print(os.chown)
    except(OSError):
        pass    
        
        
def asyncio_server2():    
    # if sys.platform != "win32":
    try:
        try:
            print(os.chown)
        except(OSError):
            print('')
    except(OSError):
        pass            

def asyncio_server3():    
    if sys.platform != "win32":
        try:
            try:
                print(os.chown)
            except(ArithmeticError, ImportError):
                print('')
        except(OSError):
            pass            
def asyncio_server4():    
    try:
        try:
            if sys.platform != "win32":
                print(os.chown)
        except(OSError):
            print('')
    except(Exception):
        pass     

def asyncio_server5():    
    try:
        try:
            if sys.platform != "win32":
                print('')
        except(OSError):
            print('')
    except(Exception):
        pass             
    os.chown
    
# OSTDetector