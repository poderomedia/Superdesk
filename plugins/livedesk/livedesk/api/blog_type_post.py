'''
Created on Aug 30, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for livedesk blog type posts.
'''

from ally.api.config import service, call, query, UPDATE
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.post.api.post import Post, QPostUnpublished
from ally.api.type import Iter
from superdesk.post.api.type import PostType
from livedesk.api.blog_type import BlogType

# --------------------------------------------------------------------

@modelLiveDesk(name=Post)
class BlogTypePost(Post):
    '''
    Provides the blog post model.
    '''
    Order = float
    BlogType = BlogType

# --------------------------------------------------------------------

@query(BlogTypePost)
class QBlogTypePost(QPostUnpublished):
    '''
    Provides the blog post message query.
    '''

# --------------------------------------------------------------------

@service
class IBlogTypePostService:
    '''
    Provides the service methods for the blog posts.
    '''

    @call
    def getById(self, blogTypeId:BlogType, postId:BlogTypePost) -> BlogTypePost:
        '''
        Provides the blog post based on the id.
        '''

    @call(webName='Posts')
    def getAll(self, blogTypeId:BlogType, typeId:PostType=None, offset:int=None,
               limit:int=None, q:QBlogTypePost=None) -> Iter(BlogTypePost):
        '''
        Provides all the blog type posts.
        '''

    @call
    def insert(self, blogTypeId:BlogType.Id, post:Post) -> BlogTypePost.Id:
        '''
        Inserts the post for the blog type.
        '''

    @call
    def update(self, blogTypeId:BlogType.Id, post:Post):
        '''
        Update the post for the blog.
        '''

    @call(method=UPDATE, webName='Reorder')
    def reorder(self, blogTypeId:BlogType.Id, postId:Post.Id, refPostId:Post.Id, before:bool=True):
        '''
        Reorder the post.
        '''

    @call
    def delete(self, id:BlogTypePost.Id) -> bool:
        '''
        Delete the post for the provided id.

        @param id: integer
            The id of the post to be deleted.

        @return: True if the delete is successful, false otherwise.
        '''
