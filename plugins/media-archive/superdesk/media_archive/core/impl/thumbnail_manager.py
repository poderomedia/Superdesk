'''
Created on Aug 3, 2012

@package: media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Thumbnail manager class definition.
'''
# --------------------------------------------------------------------

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.session import SessionSupport
from ally.support.util_io import timestampURI
from cdm.spec import ICDM, PathNotFound
from collections import OrderedDict
from os.path import splitext
from superdesk.media_archive.api.meta_data import MetaData
from superdesk.media_archive.core.spec import IThumbnailManager, \
    IThumbnailProcessor
from superdesk.media_archive.meta.meta_data import ThumbnailFormat
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IThumbnailManager)
class ThumbnailManagerAlchemy(SessionSupport, IThumbnailManager):
    '''
    Implementation for @see: IThumbnailManager
    '''
    original_name = 'original'; wire.config('original_name', doc='''
    Provides the size name for the original sized images from which the thumbnails are created''')
    thumbnail_sizes = {'tiny' : [16, 16], 'small' : [32, 32], 'medium' : [64, 64],
                       'large' : [128, 128], 'huge' : [256, 256]}; wire.config('thumbnail_sizes', doc='''
    This is basically just a simple dictionary{string, tuple(integer, integer)} that has as key a path safe name and as
    a value a tuple with the width/height of the thumbnail, example: {'small': [100, 100]}.
    ''')
    thumbnailProcessor = IThumbnailProcessor; wire.entity('thumbnailProcessor')
    cdm = ICDM
    # the content delivery manager where to publish thumbnails

    def __init__(self):
        assert isinstance(self.original_name, str), 'Invalid original name %s' % self.original_name
        assert isinstance(self.thumbnail_sizes, dict), 'Invalid thumbnail sizes %s' % self.thumbnail_sizes
        assert isinstance(self.thumbnailProcessor, IThumbnailProcessor), \
        'Invalid thumbnail processor %s' % self.thumbnailProcessor
        assert isinstance(self.cdm, ICDM), 'Invalid thumbnail CDM %s' % self.cdm

        # We order the thumbnail sizes in descending order
        thumbnailSizes = [(key, sizes) for key, sizes in self.thumbnail_sizes.items()]
        thumbnailSizes.sort(key=lambda pack: pack[1][0] * pack[1][1])
        self.thumbnailSizes = OrderedDict(thumbnailSizes)
        self._cache_thumbnail = {}

    def putThumbnail(self, thumbnailFormatId, imagePath, metaData=None):
        '''
        @see IThumbnailManager.putThumbnail
        '''
        assert isinstance(thumbnailFormatId, int), 'Invalid thumbnail format identifier %s' % thumbnailFormatId
        assert isinstance(imagePath, str), 'Invalid file path %s' % imagePath

        thumbPath = self.thumbnailPath(thumbnailFormatId, metaData)
        try: thumbTimestamp = self.cdm.getTimestamp(thumbPath)
        except PathNotFound: thumbTimestamp = None

        if not thumbTimestamp or thumbTimestamp < timestampURI(imagePath):
            imageExt, thumbProcPath = splitext(imagePath)[1], thumbPath
            thumbName, thumbExt = splitext(thumbPath)
            if imageExt != thumbExt: thumbPath = thumbName + imageExt

            self.cdm.publishFromFile(thumbPath, imagePath)

            if thumbPath != thumbProcPath:
                thumbPath, thumbProcPath = self.cdm.getURI(thumbPath, 'file'), self.cdm.getURI(thumbProcPath, 'file')
                self.thumbnailProcessor.processThumbnail(thumbPath, thumbProcPath)

    def populate(self, metaData, scheme, size=None):
        '''
        @see: IMetaDataReferencer.populate
        '''
        assert isinstance(metaData, MetaData), 'Invalid metaData %s' % metaData
        assert not size or isinstance(size, str) and size in self.thumbnailSizes, 'Invalid size value %s' % size

        if not metaData.thumbnailFormatId: return metaData

        thumbPath = self.thumbnailPath(metaData.thumbnailFormatId, metaData, size)
        try: self.cdm.getTimestamp(thumbPath)
        except PathNotFound:
            original = self.thumbnailPath(metaData.thumbnailFormatId, metaData)
            original = self.cdm.getURI(original, 'file')

            width, height = self.thumbnailSizes[size]
            self.thumbnailProcessor.processThumbnail(original, self.cdm.getURI(thumbPath, 'file'), width, height)

        metaData.Thumbnail = self.cdm.getURI(thumbPath, scheme)
        return metaData

    # ----------------------------------------------------------------

    def thumbnailPath(self, thumbnailFormatId, metaData=None, size=None):
        '''
        Construct the reference based on the provided parameters.
        '''
        format = self._cache_thumbnail.get(thumbnailFormatId)
        if format is None:
            thumbnailFormat = self.session().query(ThumbnailFormat).get(thumbnailFormatId)
            assert isinstance(thumbnailFormat, ThumbnailFormat), 'Invalid thumbnail format id %s' % thumbnailFormatId
            format = self._cache_thumbnail[thumbnailFormat.id] = thumbnailFormat.format

        keys = dict(size=size or self.original_name)
        if metaData is not None:
            assert isinstance(metaData, MetaData), 'Invalid meta data %s' % metaData

            keys.update(id=metaData.Id, file=metaData.Name, name=splitext(metaData.Name)[0])

        return format % keys
