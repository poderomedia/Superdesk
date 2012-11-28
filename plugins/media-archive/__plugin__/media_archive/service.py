'''
Created on Apr 25, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services setups for media archive superdesk.
'''

from ..cdm.local_cdm import server_uri, repository_path
from ..plugin.registry import registerService
from ..superdesk import service
from ..superdesk.db_superdesk import bindSuperdeskSession, createTables
from ally.container import ioc, support
from cdm.impl.local_filesystem import LocalFileSystemCDM, HTTPDelivery, \
    IDelivery
from cdm.spec import ICDM
from cdm.support import ExtendPathCDM
from superdesk.media_archive.api.meta_data import IMetaDataService, \
    IMetaDataUploadService
from superdesk.media_archive.api.query_criteria import IQueryCriteriaService
from superdesk.media_archive.core.impl.query_service_creator import \
    createService
from superdesk.media_archive.core.impl.thumbnail_manager import \
    ThumbnailManagerAlchemy
from superdesk.media_archive.core.spec import IThumbnailManager, QueryIndexer
from superdesk.media_archive.impl.meta_data import IMetaDataHandler, \
    MetaDataServiceAlchemy
from superdesk.media_archive.impl.query_criteria import QueryCriteriaService
import logging
from superdesk.media_archive.api.meta_info import IMetaDataInfoService
from superdesk.media_archive.impl.meta_info import MetaDataInfoService

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def addMetaDataHandler(handler):
    if not isinstance(handler, IMetaDataService): metaDataHandlers().append(handler)

support.createEntitySetup('superdesk.media_archive.core.impl.**.*')
support.bindToEntities('superdesk.media_archive.core.impl.**.*Alchemy', binders=bindSuperdeskSession)
support.listenToEntities(IMetaDataHandler, listeners=addMetaDataHandler, beforeBinding=False, module=service)
loadAllMetaDataHandlers = support.loadAllEntities(IMetaDataHandler, module=service)

# --------------------------------------------------------------------

@ioc.entity
def delivery() -> IDelivery:
    d = HTTPDelivery()
    d.serverURI = server_uri()
    d.repositoryPath = repository_path()
    return d

@ioc.entity
def contentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemCDM();
    cdm.delivery = delivery()
    return cdm

@ioc.entity
def cdmArchive() -> ICDM:
    '''
    The content delivery manager (CDM) for the media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/%s')

@ioc.entity
def cdmThumbnail() -> ICDM:
    '''
    The content delivery manager (CDM) for the thumbnails media archive.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'media_archive/thumbnail/%s')

@ioc.replace(ioc.getEntity(IThumbnailManager))
def thumbnailManager() -> IThumbnailManager:
    b = ThumbnailManagerAlchemy()
    b.cdm = cdmThumbnail()
    return b

@ioc.entity
def metaDataHandlers(): return []

@ioc.replace(ioc.getEntity(IMetaDataUploadService, service))
def metaDataService() -> IMetaDataUploadService:
    b = MetaDataServiceAlchemy()
    b.cdmArchive = cdmArchive()
    b.metaDataHandlers = metaDataHandlers()
    return b

@ioc.replace(ioc.getEntity(IMetaDataInfoService, service))
def metaDataInfoService() -> IMetaDataInfoService:
    b = MetaDataInfoService()
    b.cdmArchive = cdmArchive()
    return b

@ioc.entity
def queryIndexer() -> QueryIndexer:
    b = QueryIndexer()
    return b

@ioc.replace(ioc.getEntity(IQueryCriteriaService, service))
def publishQueryCriteriaService() -> IQueryCriteriaService:
    b = QueryCriteriaService(queryIndexer())
    return b

# --------------------------------------------------------------------

@ioc.after(loadAllMetaDataHandlers, createTables)
def publishQueryService():
    b = createService(queryIndexer())
    registerService(b, (bindSuperdeskSession,))

@ioc.after(loadAllMetaDataHandlers, createTables)
def deploy():
    metaDataService().deploy()


