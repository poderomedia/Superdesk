'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog collaborator.
'''

from .blog import Blog
from ally.api.config import service, call, INSERT, DELETE
from ally.api.type import Iter
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.collaborator.api.collaborator import Collaborator

# --------------------------------------------------------------------

@modelLiveDesk(name=Collaborator)
class BlogCollaborator(Collaborator):
    '''
    Provides the blog collaborator model.
    '''
    Blog = Blog

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service
class IBlogCollaboratorService:
    '''
    Provides the service methods for the blog collaborators.
    '''

    @call
    def getById(self, blogId:Blog, collaboratorId:BlogCollaborator) -> BlogCollaborator:
        '''
        Provides the blog collaborator based on the id.
        '''

    @call
    def getAll(self, blogId:Blog) -> Iter(BlogCollaborator):
        '''
        Provides all the blog collaborators.
        '''

    @call(method=INSERT, webName='Add')
    def addCollaborator(self, blogId:Blog.Id, collaboratorId:Collaborator.Id) -> BlogCollaborator.Id:
        '''
        Assigns the collaborator as a collaborator to the blog.
        '''

    @call(method=DELETE, webName='Remove')
    def removeCollaborator(self, blogId:Blog, collaboratorId:Collaborator) -> bool:
        '''
        Removes the collaborator from the blog.
        '''
