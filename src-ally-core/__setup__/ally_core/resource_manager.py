'''
Created on Nov 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the resource manager.
'''

from .assembler import assemblers
from ally import ioc
from ally.core.impl.resources_manager import ResourcesManagerImpl

# --------------------------------------------------------------------
# Creating the resource manager

@ioc.entity
def services(): return []

@ioc.entity
def resourcesManager() -> ResourcesManagerImpl:
    b = ResourcesManagerImpl()
    b.assemblers = assemblers()
    b.services = services()
    return b