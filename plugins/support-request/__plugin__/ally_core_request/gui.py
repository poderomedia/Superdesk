'''
Created on Feb 2, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the GUI configuration setup for the node presenter plugin.
'''

from ..plugin.registry import cdmGUI
from ally.container import ioc
import os

# --------------------------------------------------------------------

@ioc.start
def publishJS():
    sysPath = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    cdmGUI().publishFromDir('js/devel', os.path.join(sysPath, 'js_gui'))