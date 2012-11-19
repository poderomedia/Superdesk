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

NAME = 'FFmpeg binary'
GROUP = 'Binaries'
VERSION = '1.0'
DESCRIPTION = '''Populates in the workspace tools the FFMpeg binary.'''

# --------------------------------------------------------------------

@ioc.config
def ffmpeg_dir_path():
    '''
    The path to the ffmpeg tools.
    '''
    return join('workspace', 'tools', 'ffmpeg')

# --------------------------------------------------------------------

@ioc.start
def deploy():
    if ffmpeg_dir_path(): deployTool(join(pythonPath(), 'resources', 'ffmpeg'), ffmpeg_dir_path())
