'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for blog API.
'''

from ..api.blog import Blog
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from superdesk.meta.metadata_superdesk import Base
from superdesk.language.meta.language import LanguageEntity
from superdesk.user.meta.user import UserMapped
from sqlalchemy.types import String, DateTime, Text
from sqlalchemy.orm import column_property
from sqlalchemy.sql.expression import select, func
from ally.support.sqlalchemy.mapper import validate
from ally.container.binder_op import validateManaged
from livedesk.meta.blog_type import BlogTypeMapped

# --------------------------------------------------------------------

@validate(exclude=('CreatedOn',))
class BlogMapped(Base, Blog):
    '''
    Provides the mapping for Blog.
    '''
    __tablename__ = 'livedesk_blog'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Type = Column('fk_blog_type', ForeignKey(BlogTypeMapped.Id), nullable=False)
    Language = Column('fk_language_id', ForeignKey(LanguageEntity.Id), nullable=False)
    Creator = Column('fk_creator_id', ForeignKey(UserMapped.Id), nullable=False)
    Title = Column('title', String(255), nullable=False)
    Description = Column('description', Text)
    OutputLink = Column('output_link', Text)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    LiveOn = Column('live_on', DateTime)
    ClosedOn = Column('closed_on', DateTime)

validateManaged(BlogMapped.CreatedOn)

# --------------------------------------------------------------------

from livedesk.meta.blog_post import BlogPostMapped
BlogMapped.UpdatedOn = column_property(select([func.max(BlogPostMapped.UpdatedOn)]).
                                       where(BlogPostMapped.Blog == BlogMapped.Id))
