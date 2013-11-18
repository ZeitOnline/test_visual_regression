from zope.interface import Interface


class IPara(Interface):

    """ Represents Paragraphs in IPage -> IContent """
    pass


class IPage(Interface):

    """ Represents Pages in IContent """
    pass


class ICitation(Interface):

    """ Represents Citation in IContent """
    pass


class IIntertitle(Interface):

    """ Represents Intertitle in IContent """
    pass


class IAdvertising(Interface):

    """ Represents Advertising in IContent """
    pass


class IImg(Interface):

    """ Represents Image in IContent """
    pass

class IMetaBox(Interface):

    """ Represents Metabox in IContent """
    pass


class IVideo(Interface):

    """ Represents Image in IContent """
    pass

class ITags(Interface):

    """ Represents Tags in IContent """
    pass

class ITag(Interface):

    """ Represents Single Tag in IContent """
    pass
