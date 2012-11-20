'''
Created on Apr 19, 2012

@package: ffmpeg binary
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Provides the ffmpeg in the workspace tools.
'''

from os.path import join
from ally.support.util_sys import pythonPath
from ally.container import ioc
from ally.support.util_deploy import deploy as deployTool

# --------------------------------------------------------------------

NAME = 'Exiv2 binary'
GROUP = 'Binaries'
VERSION = '1.0'
DESCRIPTION = '''Populates in the workspace tools the Exiv2 binary.'''

# --------------------------------------------------------------------

@ioc.config
def exiv2_dir_path():
    '''
    The path to the exiv2 tools.
    '''
    return join('workspace', 'tools', 'exiv2')

# --------------------------------------------------------------------

@ioc.start
def deploy():
    if exiv2_dir_path(): deployTool(join(pythonPath(), 'resources', 'exiv2'), exiv2_dir_path())
