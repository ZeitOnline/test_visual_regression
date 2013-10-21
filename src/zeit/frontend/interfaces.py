from zope.interface import Interface


class IPara(Interface):
    """ Represents Paragraphs in IPage -> IContent """
    pass


class IPage(Interface):
    """ Represents Pages in IContent """
    pass


class IBlockquote(Interface):
    """ Represents Blockquote in IContent """
    pass


class IIntertitle(Interface):
    """ Represents Intertitle in IContent """
    pass


class IImg(Interface):
    """ Represents Image in IContent """
    pass


class IVideo(Interface):
    """ Represents Image in IContent """
    pass
