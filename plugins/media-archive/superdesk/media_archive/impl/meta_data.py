'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the meta data API.
'''

from ..api.meta_data import QMetaData
from ..core.impl.meta_service_base import MetaDataServiceBaseAlchemy
from ..core.spec import IMetaDataHandler, IMetaDataReferencer, IThumbnailManager
from ..meta.meta_data import MetaDataMapped
from ally.api.model import Content
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.exception import InputError
from ally.internationalization import _
from ally.support.sqlalchemy.util_service import handle
from ally.support.util_sys import pythonPath
from cdm.spec import ICDM
from os.path import join, getsize, abspath
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.functions import current_timestamp
from superdesk.media_archive.api.meta_data import IMetaDataUploadService
from superdesk.media_archive.core.impl.meta_service_base import metaTypeFor, \
    thumbnailFormatFor
from superdesk.media_archive.meta.meta_data import META_TYPE_KEY

# --------------------------------------------------------------------

@injected
@setup(IMetaDataUploadService)
class MetaDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer, IMetaDataUploadService):
    '''
    Implementation for @see: IMetaDataService, and also provides services as the @see: IMetaDataReferencer
    '''

    format_file_name = '%(id)s.%(name)s'; wire.config('format_file_name', doc='''
    The format for the files names in the media archive''')
    format_thumbnail = '%(size)s/other.jpg'; wire.config('format_thumbnail', doc='''
    The format for the unknown thumbnails in the media archive''')

    cdmArchive = ICDM
    # The archive CDM.
    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')
    # Provides the thumbnail referencer
    metaDataHandlers = list
    # The handlers list used by the meta data in order to get the references.

    def __init__(self):
        '''
        Construct the meta data service.
        '''
        assert isinstance(self.format_file_name, str), 'Invalid format file name %s' % self.format_file_name
        assert isinstance(self.format_thumbnail, str), 'Invalid format thumbnail %s' % self.format_thumbnail
        assert isinstance(self.cdmArchive, ICDM), 'Invalid archive CDM %s' % self.cdmArchive
        assert isinstance(self.thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % self.thumbnailManager
        assert isinstance(self.metaDataHandlers, list), 'Invalid reference handlers %s' % self.referenceHandlers

        MetaDataServiceBaseAlchemy.__init__(self, MetaDataMapped, QMetaData, self)

    def deploy(self):
        '''
        Deploy the meta data and all handlers.
        '''
        self._thumbnailFormat = thumbnailFormatFor(self.session(), self.format_thumbnail)
        self.thumbnailManager.putThumbnail(self._thumbnailFormat.id, abspath(join(pythonPath(), 'resources', 'other.jpg')))
        self._metaType = metaTypeFor(self.session(), META_TYPE_KEY)

        for handler in self.metaDataHandlers:
            assert isinstance(handler, IMetaDataHandler), 'Invalid meta data handler %s' % handler
            handler.deploy()

    # ----------------------------------------------------------------

    def populate(self, metaData, scheme, thumbSize=None):
        '''
        @see: IMetaDataReferencer.populate
        '''
        assert isinstance(metaData, MetaDataMapped), 'Invalid meta data %s' % metaData
        metaData.Content = self.cdmArchive.getURI(metaData.content, scheme)
        return self.thumbnailManager.populate(metaData, scheme, thumbSize)

    # ----------------------------------------------------------------

    def insert(self, userId, content):
        '''
        @see: IMetaDataService.insert
        '''
        assert isinstance(content, Content), 'Invalid content %s' % content
        if not content.name: raise InputError(_('No name specified for content'))

        metaData = MetaDataMapped()
        metaData.CreatedOn = current_timestamp()
        metaData.Creator = userId
        metaData.Name = content.name

        metaData.typeId = self._metaType.Id
        metaData.thumbnailFormatId = self._thumbnailFormat.id

        try:
            self.session().add(metaData)
            self.session().flush((metaData,))

            path = self.format_file_name % {'id': metaData.Id, 'name': metaData.Name}
            path = ''.join((META_TYPE_KEY, '/', self.generateIdPath(metaData.Id), '/', path))
            contentPath = self.cdmArchive.getURI(path, 'file')

            self.cdmArchive.publishContent(path, content)
            metaData.content = path
            metaData.SizeInBytes = getsize(contentPath)

            for handler in self.metaDataHandlers:
                assert isinstance(handler, IMetaDataHandler), 'Invalid handler %s' % handler
                if handler.processByInfo(metaData, contentPath, content.type): break
            else:
                for handler in self.metaDataHandlers:
                    if handler.process(metaData, contentPath): break

            self.session().merge(metaData)
            self.session().flush((metaData,))
        except SQLAlchemyError as e: handle(e, metaData)


        if metaData.content != path:
            self.cdmArchive.republish(path, metaData.content)

        return metaData.Id

    # ----------------------------------------------------------------

    def generateIdPath (self, id):
        return '{0:03d}'.format((id // 1000) % 1000)
