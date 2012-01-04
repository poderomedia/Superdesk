'''
Created on Jun 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides implementations that provide general behavior or functionality.
'''

from inspect import isclass
import sys

# --------------------------------------------------------------------

# Flag indicating that the python version is 3k or more.
IS_PY3K = int(sys.version[:1]) >= 3

# --------------------------------------------------------------------

class Uninstantiable:
    '''
    Extending this class will not allow for the creation of any instance of the class.
    This has to be the first class inherited in order to properly work.
    '''
    
    def __new__(cls, *args, **keyargs):
        '''
        Does not allow you to create an instance.
        '''
        raise Exception('Cannot create an instance of %r class' % cls.__name__)

# --------------------------------------------------------------------

class Singletone:
    '''
    Extending this class will always return the same instance.
    '''
    
    def __new__(cls):
        '''
        Will always return the same instance.
        '''
        if not hasattr(cls, '_UTIL_singletone'):
            cls._UTIL_singletone = super().__new__(cls)
        return cls._UTIL_singletone

# --------------------------------------------------------------------

_NAME_IDS = {}
# Used by the attribute to assign a unique id to a name.

_NAME_ID = lambda name: str(_NAME_IDS.setdefault(name, len(_NAME_IDS)))
# Provides the name id.

class Attribute:
    '''
    Class used for creating attributes for python objects. The purpose of this is not to directly use the the __dict__
    or getattr in order to store values in order to avoid name clashes.
    '''
    
    def __init__(self, group, name, valueType=None):
        '''
        Creates a new attribute.
        
        @param group: string
            The group name for the attribute, this is usually the module name where is created, it helps to distinguish
            between same names but with other purposes.
        @param name: string
            The name of the attribute.
        @param valueType: type
            The type to check for the set and get values.
        '''
        assert isinstance(group, str), 'Invalid group name %s' % group
        assert isinstance(name, str), 'Invalid name %s' % name
        assert not valueType or isclass(valueType), 'Invalid value type %s' % valueType
        self.__group = group
        self.__name = name
        self.__type = valueType
        if __debug__: self.__id = group + '.' + name
        else:
            self.__id = _NAME_ID(group) + '_' + _NAME_ID(name)
    
    def has(self, obj):
        '''
        Checks if there is a value for the provided object.
        
        @param obj: object
            The object to check for value.
        @return: boolean
            true if there is a value, False otherwise.
        '''
        assert obj is not None, 'An object is required'
        return hasattr(obj, self.__id)
    
    def get(self, obj, *default):
        '''
        Get the value from the provided object.
        
        @param obj: object
            The object to get the value from.
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        assert obj is not None, 'An object is required'
        value = getattr(obj, self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def set(self, obj, value):
        '''
        Sets the value to the provided object.
        
        @param obj: object
            The object to set the value to.
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert obj is not None, 'An object is required'
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        setattr(obj, self.__id, value)
        return value
        
    def delete(self, obj):
        '''
        Deletes the value from the provided object.
        
        @param obj: object
            The object to delete the value from.
        '''
        assert obj is not None, 'An object is required'
        delattr(obj, self.__id)
        
    def hasOwn(self, obj):
        '''
        Checks if there is a value for the provided object by using __dict__.
        
        @param obj: object
            The object to check for value.
        @return: boolean
            true if there is a value, False otherwise.
        '''
        assert obj is not None, 'An object is required'
        return self.__id in obj.__dict__
    
    def getOwn(self, obj, *default):
        '''
        Get the value from the provided object by using __dict__.
        
        @param obj: object
            The object to get the value from.
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        assert obj is not None, 'An object is required'
        value = obj.__dict__.get(self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def setOwn(self, obj, value):
        '''
        Sets the value to the provided object by using __dict__.
        
        @param obj: object
            The object to set the value to.
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert obj is not None, 'An object is required'
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        obj.__dict__[self.__id] = value
        return value
        
    def deleteOwn(self, obj):
        '''
        Deletes the value from the provided object by using __dict__.
        
        @param obj: object
            The object to delete the value from.
        '''
        assert obj is not None, 'An object is required'
        del obj.__dict__[self.__id]
        
    def hasDict(self, map):
        '''
        Checks if there is a value for the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to check for value.
        @return: boolean
            true if there is a value, False otherwise.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        return self.__id in map
    
    def getDict(self, map, *default):
        '''
        Get the value from the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to get the value from.
        @param default: argument
            If provided will return the default if no argument value is available.
        @return: object
            The value.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        value = map.get(self.__id, *default)
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to get for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        return value
    
    def setDict(self, map, value):
        '''
        Sets the value to the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to set the value to.
        @param value: object
            The value to set.
        @return: object
            The provided value.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        assert not(self.__type and value is not None) or isinstance(value, self.__type), 'Invalid value %s to set for ' \
        'required type %s, for attribute %s.%s' % (value, self.__type, self.__group, self.__name)
        map[self.__id] = value
        return value
        
    def deleteDict(self, map):
        '''
        Deletes the value from the provided map dictionary.
        
        @param map: dictionary
            The map dictionary to delete the value from.
        '''
        assert isinstance(map, dict), 'Invalid map %s' % map
        del map[self.__id]