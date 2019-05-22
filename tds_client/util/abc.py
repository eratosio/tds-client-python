
from abc import ABCMeta, abstractmethod

ABC = ABCMeta('ABC', (object,), {'__slots__': ()})  # compatible with Python 2 *and* 3
