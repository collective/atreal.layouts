from AccessControl import getSecurityManager
from DateTime import DateTime

from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.interface import Interface, implements

from persistent.mapping import PersistentMapping

from plone.app.layout.viewlets.content import DocumentBylineViewlet
from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IModificationLister(Interface):
    """List of recent modifications.
    """

    def update(self):
        """ """

    def last(self):
        """ """


class ModificationLister(object):

    implements(IModificationLister)

    _modifications = None

    def __init__(self, context):
        """ """
        self.context = context

    @property
    def modifications(self):
        """ Handle storage for the modification list """
        key = self.__class__.__name__
        if self._modifications is None:
            annotations = IAnnotations(self.context)
            if not annotations.has_key(key):
                annotations[key] = PersistentMapping()
            self._modifications = annotations[key]
        return self._modifications

    def update(self):
        """ Update the author of the last modification """
        gsm = getSecurityManager()
        user = gsm.getUser()
        if user:
            author = user.getId()
            self.modifications['last_modifier_name'] = author

    @property
    def last_modifier_name(self):
        """ Get the last modification info from the modifications list """
        if not len(self.modifications):
            return
        try:
            return self.modifications['last_modifier_name']
        except AttributeError:
            return


class CustomDocumentByLineViewlet(DocumentBylineViewlet):

    index = ViewPageTemplateFile("document_by_line.pt")

    def update(self):
        DocumentBylineViewlet.update(self)
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.tools = getMultiAdapter((self.context, self.request),
                                     name='plone_tools')
        self.modifier = self.last_modification()

    # @memoize
    def last_modification(self):
        if IPloneSiteRoot.providedBy(self.context):
            # We are on the plone site root
            return
        return IModificationLister(self.context).last_modifier_name
        
    # @memoize
    def modifiername(self):
        if self.modifier:
            membership = self.tools.membership()
            modifier = membership.getMemberInfo(self.modifier)
            return modifier and modifier['fullname'] or \
                self.modifier
        return None


def modificationNotifier(obj, event):
    """ Handle storage of last modifier at each modification """
    IModificationLister(obj).update()

