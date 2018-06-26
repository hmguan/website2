from functools import wraps

def singleton(cls,*args,**kwargs):
    instances={}
    @wraps(cls)
    def _singleton():
        if cls not in instances:
            instances[cls]=cls(*args,**kwargs)
        return instances[cls]
    return _singleton