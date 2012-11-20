'''
Created on Aug 2, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for languages.
'''

from ally.api.config import service, call, query, LIMIT_DEFAULT
from ally.api.criteria import AsLikeOrdered
from ally.api.type import Locale, List, Iter
from superdesk.api.domain_superdesk import modelSuperDesk

# --------------------------------------------------------------------

@modelSuperDesk(id='Code')
class Country:
    '''    
    Provides the country model.
    '''
    Code = str
    Name = str

    def __init__(self, Code=None, Name=None):
        if Code: self.Code = Code
        if Name: self.Name = Name

# --------------------------------------------------------------------

@query(Country)
class QCountry:
    '''
    Provides the country query model.
    '''
    name = AsLikeOrdered
    code = AsLikeOrdered

# --------------------------------------------------------------------

@service
class ICountryService:
    '''
    Provides services for country.
    '''

    @call
    def getByCode(self, code:Country.Code, locales:List(Locale)=()) -> Country:
        '''
        Provides the countries having the specified code.
        '''

    @call
    def getAllAvailable(self, locales:List(Locale)=(), offset:int=None, limit:int=LIMIT_DEFAULT,
                        q:QCountry=None) -> Iter(Country):
        '''
        Provides all the available countries.
        '''
