import os 

def with_try_simple():    
    try:
        print(os.chown)
    except(OSError):
        pass    

def with_try_two_exception():    
    try:
        print(os.fork())
    except(OSError, Exception):
        pass    

def with_two_try_nested():    
    try:
        try:
            print(os.getgid())
        except(OSError):
            print('')
    except(OSError):
        pass      
       
def with_two_try_nested_distinct_exception():    
    try:
        try:
            print(os.get_blocking(0))
        except(ArithmeticError, ImportError):
            print('')
    except(OSError):
        pass         
 