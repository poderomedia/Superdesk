'''
Created on May 2, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for posts.
'''

from ally.api.authentication import auth
from ally.api.config import service, call, query, LIMIT_DEFAULT
from ally.api.criteria import AsDateTimeOrdered, AsBoolean
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityGetCRUDService
from ally.support.api.keyed import QEntity
from datetime import datetime
from superdesk.api.domain_superdesk import modelSuperDesk
from superdesk.collaborator.api.collaborator import Collaborator
from superdesk.post.api.type import PostType
from superdesk.user.api.user import User

# --------------------------------------------------------------------

@modelSuperDesk
class Post(Entity):
    '''
    Provides the post message model.
    '''
    Type = PostType
    Creator = auth(User)
    Author = Collaborator
    IsModified = bool
    Meta = str
    ContentPlain = str
    Content = str
    CreatedOn = datetime
    PublishedOn = datetime
    UpdatedOn = datetime
    DeletedOn = datetime
    AuthorName = str

# --------------------------------------------------------------------

@query(Post)
class QPostUnpublished(QEntity):
    '''
    Provides the post message query.
    '''
    createdOn = AsDateTimeOrdered
    isModified = AsBoolean
    updatedOn = AsDateTimeOrdered
    deletedOn = AsDateTimeOrdered

@query(Post)
class QPostPublished(QPostUnpublished):
    '''
    Provides the post message query.
    '''
    publishedOn = AsDateTimeOrdered

@query(Post)
class QPost(QPostPublished):
    '''
    Provides the post message query.
    '''
    deletedOn = AsDateTimeOrdered

# --------------------------------------------------------------------

@service((Entity, Post))
class IPostService(IEntityGetCRUDService):
    '''
    Provides the service methods for the post.
    '''

    @call(webName='Unpublished')
    def getUnpublished(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None,
                       limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QPostUnpublished=None) -> Iter(Post):
        '''
        Provides all the unpublished posts.
        '''

    @call(webName='Published')
    def getPublished(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None,
                     limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QPostPublished=None) -> Iter(Post):
        '''
        Provides all the published posts.
        '''

    @call
    def getAll(self, creatorId:User.Id=None, authorId:Collaborator.Id=None, offset:int=None, limit:int=LIMIT_DEFAULT,
               detailed:bool=True, q:QPost=None) -> Iter(Post):
        '''
        Provides all the posts.
        '''
