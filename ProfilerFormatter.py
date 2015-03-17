__author__ = 'jan-hybs'
import abc

class ProfilerFormatter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def format (self, json):
        """Method for transformation json to other format"""
        return