from plone.indexer.decorator import indexer
from zope.component.exceptions import ComponentLookupError

# from atreal.deadline.interfaces import IDeadlineable, IDeadlineAware
from Products.ATContentTypes.interface.interfaces import IATContentType
from atreal.layouts.browser.document_by_line import IModificationLister


@indexer(IATContentType)  
def last_modifier_indexer(obj):
  try:
    last_modifier = IModificationLister(obj).last_modifier_name
    if not last_modifier:
      raise AttributeError
    return last_modifier
  except (ComponentLookupError, TypeError, ValueError):
    # The catalog expects AttributeErrors when a value can't be found
    raise AttributeError
