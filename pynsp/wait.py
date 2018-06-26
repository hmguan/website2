"""
waitable_handle transplant from libnsp, the c++ framwork
"""

from threading import Lock
from threading import Condition

def scoped_lock(_Locker):
    def __scoped_lock(fn):       
        def inner(*args, **kwargs):
            _Locker.acquire()
            retval = fn(*args, **kwargs)
            _Locker.release()
            return retval
        return inner
    return __scoped_lock

class waitable_handle(object):
    """
    class waitable_handle Provide a common thread synchronization and notification mechanism
    """

    def __init__(self, _sync=True):
        """
        if _sync is True, behavior of object of this class is synchronous event
        otherwise, behavior of object of this class is notification event
        """
        self.__mutex = Lock()
        self.__cond = Condition(self.__mutex)
        self.__sync = _sync
        self.__pass = False

    def __del__(self):
        pass

    def __wait(self, timeout)->bool:
        # wait util signal.
        if timeout <= 0:
            self.__cond.wait()
        # wait signal or timeout
        else:
            retval = self.__cond.wait(float(timeout / 1000))
            if not retval: # wait timeout
                return False
        return True

    # @timeout in milliseconds
    def wait(self, timeout=0)->bool:
        """
        wait for current thread to be awakened or milliseconds specify by timeout has been elapsed
        """
        retval = True
        self.__mutex.acquire()

        if self.__sync:
            self.__pass = False
            while not self.__pass:
                retval = self.__wait(timeout)
                if not retval:
                    break
            self.__pass = False
        else:
            if not self.__pass:
                retval = self.__wait(timeout)

        self.__mutex.release()
        return retval

    def sig(self):
        """
        the thread which waitting for this object block on method @wait will be awakened
        """
        self.__mutex.acquire()
        self.__pass = True
        if self.__sync:
            self.__cond.notify()
        else:
            self.__cond.notify_all()
        self.__mutex.release()

    def reset(self):
        """
        reset states of this object to no-signal states.
        only when the behavior of current object is notification event
        """
        if not self.__sync:
            self.__mutex.acquire()
            self.__pass = False
            self.__mutex.release()
