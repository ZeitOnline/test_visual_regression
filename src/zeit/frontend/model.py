from lxml import objectify, etree
from os.path import isdir
from os.path import isfile
from zope.interface import implementer
from zeit.frontend import interfaces
import pkg_resources
import iso8601


class Resource(object):
    pass


class Directory(Resource):
    base_path = ''

    def __init__(self, base_path):
        self.base_path = base_path

    def __getitem__(self, name):
        path = self.base_path + '/' + name
        if isdir(path):
            return Directory(path)
        if isfile(path):
            return Content(path)
        else:
            raise KeyError


def get_root(request):
    return Directory(pkg_resources.resource_filename(__name__, 'data'))


class Content (Resource):
    title = ''
    subtitle = ''
    teaser_title = ''
    teaser_text = ''
    pages = []
    header_img_src = ''
    lead_pic = ''
    author = ''
    publish_date = ''
    rankedTags = []
    genre = ''
    source = ''
    subpage_index = []

    def __json__(self, request):
        return dict((name, getattr(self, name)) for name in dir(self)
                    if not name.startswith('__'))

    def __init__(self, path):
        article_tree = objectify.parse(path)
        root = article_tree.getroot()
        self.title = unicode(root.body.title)
        self.subtitle = unicode(root.body.subtitle)
        self.supertitle = unicode(root.body.supertitle)
        self.__construct_pages(root)
        self.__extract_header_img(root)
        self.teaser_title = unicode(article_tree.getroot().teaser.title)
        self.teaser_text = unicode(article_tree.getroot().teaser.text)
        dpth = "//attribute[@name='date_first_released']"
        pdate = root.head.xpath(dpth).pop().text
        self.publish_date = iso8601.parse_date(pdate)
        self.__construct_tags(root)
        self.rankedTags = self.__construct_tags(root)
        self.source = self.__construct_source(root)
        self.genre = self.__construct_genre(root)
        self.location = self.__construct_location(root)
        self.author = self.__construct_author(root)

    def __construct_author(self, root):
        try:
            author = {'name': unicode(root.head.author.display_name)}
            url = root.head.author.xpath("@href")
            if len(url) > 0:
                author['href'] = url.pop()
            author['prefix'] = " von " if self.genre else "Von "
            if self.location:
                author['suffix'] = ", "
            return author
        except AttributeError:
            return

    def __construct_source(self, root):
        try:
            copyright = root.head.xpath("//attribute[@name='copyrights']")

            if copyright:
                return copyright
            else:
                return self.__construct_product_id(root)

        except AttributeError:
            return __construct_product_id(root)

    def __construct_product_id(self, root):
        try:
            product_id = root.head.xpath("//attribute[@name='product-id']")
            path = 'config/products.xml'
            products_path = pkg_resources.resource_filename(__name__, path)
            products_tree = objectify.parse(products_path)
            products_root = products_tree.getroot()

            if product_id:

                expr = "//product[@id='%s']/@title" % (product_id[0])
                product_name = products_root.xpath(expr)

                return product_name[0]

            else:
                return

        except AttributeError:
            return

    def __construct_location(self, root):
        try:
            return root.head.xpath("//attribute[@name='location']").pop()
        except IndexError:
            return

    def __construct_tags(self, root):
        try:
            return _get_tags(root.head.rankedTags)
        except AttributeError:
            return

    def __construct_genre(self, root):
        genres = root.head.xpath("//attribute[@name='genre']")
        path = "config/article-genres.xml"
        if len(genres) > 0:
            gconf = pkg_resources.resource_filename(__name__, path)
            gtree = objectify.parse(gconf)
            groot = gtree.getroot()
            expr = "//genre[@name='%s' and @display-frontend='true']/@prose" %\
                (genres.pop(0))
            return groot.xpath(expr).pop(0)

    def __construct_pages(self, root):
        pages = root.body.xpath("//division[@type='page']")
        self.pages = _get_pages(pages)
        self.subpage_index = self.__construct_subpage_index(self.pages)

    def __construct_subpage_index(self, pages):
        index = []
        for page in pages:
            try:
                string = "%i - %s" % (page.number, page.teaser)
                index.append(string)
            except AttributeError:
                pass
        return index

    def __extract_header_img(self, root):
        try:
            first_img = root.body.find('division').find('image')
            if (first_img.get('layout') == 'zmo_header'):
                self.header_img = Img(first_img)
        except AttributeError:
            return


@implementer(interfaces.IPage)
class Page(object):
    __content = []

    def __init__(self, page_xml):
        self.__content = iter(self._extract_items(page_xml))
        self.number = page_xml.number
        if page_xml.get('teaser') is not None:
            self.teaser = page_xml.get('teaser')

    def __iter__(self):
        return self.__content

    def _extract_items(self, page_xml):
        content = []
        add_meta = False

        for item in page_xml.iterchildren():
            if item.tag == 'p':
                content.append(Para(item))
            if item.tag == 'intertitle':
                content.append(Intertitle(item))
            if item.tag == 'image' and item.get('layout') != 'zmo_header':
                content.append(Img(item))
            if item.tag == 'citation':
                content.append(Citation(item))
            if item.tag == 'advertising':
                content.append(Advertising(item))
        #content = __insert_metabox(content)
        return content


def __insert_metabox(c):
    c.insert(c.index(next(obj for obj in c if type(obj) == Para)), Metabox())
    return c


@implementer(interfaces.IMetaBox)
class Metabox(object):
    def __init__(self):
        pass


@implementer(interfaces.IPara)
class Para(object):

    def __init__(self, xml):
        self.html = _inline_html(xml)

    def __str__(self):
        return unicode(self.html)


@implementer(interfaces.IImg)
class Img(object):

    def __init__(self, xml):
        self.src = xml.get('src')
        self.align = xml.get('align')
        self.caption = _inline_html(xml.find('bu'))
        self.copyright = _inline_html(xml.find('copyright'))
        self.layout = xml.get('layout')


@implementer(interfaces.IIntertitle)
class Intertitle(object):

    def __init__(self, xml):
        self.text = unicode(xml.text)

    def __str__(self):
        return self.text


@implementer(interfaces.ICitation)
class Citation(object):

    def __init__(self, xml):
        self.url = xml.get('url')
        self.attribution = xml.get('attribution')
        self.text = xml.get('text')
        self.layout = xml.get('layout')


@implementer(interfaces.IAdvertising)
class Advertising(object):

    def __init__(self, xml):
        self.type = unicode(xml.get('type'))

    def __str__(self):
        return self.type


@implementer(interfaces.IVideo)
class Video(object):

    def __init__(self, xml):
        pass


@implementer(interfaces.ITags)
class Tags(object):

    __content = []

    def __init__(self, tag_xml):
        self.__content = iter(self._extract_items(tag_xml))

    def __iter__(self):
        return self.__content

    def _extract_items(self, tag_xml):
        content = []
        for item in tag_xml.iterchildren():
            content.append(Tag(item))
        return content


@implementer(interfaces.ITag)
class Tag(object):

    def __init__(self, xml):
        self.html = _inline_html(xml)
        self.url = xml.get('url_value')

    def __str__(self):
        return unicode(self.html)


def _get_pages(pages_xml):
    pages = []
    number = 0
    for page in pages_xml:
        page.number = number
        number = number + 1
        pages.append(Page(page))
    return pages


def _get_tags(tags_xml):
    tags = []
    for tag in tags_xml:
        tags.append(Tags(tag))
    return tags


def _inline_html(xml):
    filter_xslt = etree.XML('''
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="xml"
                        omit-xml-declaration="yes" />
            <xsl:template match="p">
                <xsl:apply-templates />
            </xsl:template>
            <xsl:template match="i">
                <i><xsl:apply-templates /></i>
            </xsl:template>
            <xsl:template match="em">
                <em><xsl:apply-templates /></em>
            </xsl:template>
            <xsl:template match="a">
                <xsl:text> </xsl:text>
                <a><xsl:apply-templates select="@* | node | text()" /> </a>
            </xsl:template>
            <xsl:template match="a/@href">
                <xsl:copy><xsl:apply-templates /></xsl:copy>
            </xsl:template>
            <xsl:template match="a/@target">
                <xsl:copy><xsl:apply-templates /></xsl:copy>
            </xsl:template>
        </xsl:stylesheet>''')
    transform = etree.XSLT(filter_xslt)
    return transform(xml)
