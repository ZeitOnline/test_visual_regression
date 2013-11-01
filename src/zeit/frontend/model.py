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
        self.author = unicode(root.head.author.display_name)
        self.teaser_title = unicode(article_tree.getroot().teaser.title)
        self.teaser_text = unicode(article_tree.getroot().teaser.text)
        dpth = "//attribute[@name='date_first_released']"
        pdate = root.head.xpath(dpth).pop().text
        self.publish_date = iso8601.parse_date(pdate)
        self.__construct_tags(root)
        self.__construct_genre(root)
        self.rankedTags = self.__construct_tags(root)
        self.source = self.__construct_source(root)

        #root.head.xpath("//attribute[@name='product-name']").pop().text
    
        #attribute[@name='copyrights']
        #attribute[@name='product-id']
            #$product-id='ZMLB
            #$productxml/product[@id=$product-id]/@href
            #$product-id='ZEI' or $product-id='ZEAR'
            #fallback: $productxml/product[@id=$product-id]

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
            base_path = pkg_resources.resource_filename(__name__, 'data')
            products_path = objectify.parse(base_path + '/config/products.xml') 
            products_root = products_path.getroot()

            if product_id:

                #product_name = root.head.xpath("//product[@id='%s']") % product_id.pop()  
                #product_name = products_root

                return #products_path.getroot().products

                #if(product_id.pop() is 'ZMLB'):
                 #   return
                #elif (product_id.pop() is 'ZEI'):
                 #   return

            else:
                return 

        except AttributeError:
            return 


    def __construct_tags(self, root):
        try:
            return _get_tags(root.head.rankedTags)
        except AttributeError:
            return

    def __construct_genre(self, root):
        rawgenre = root.head.xpath("//attribute[@name='genre']")
        if len(rawgenre) > 0:
            genreconfig = pkg_resources.resource_filename(__name__, "config/article-genres.xml")
            genretree = objectify.parse(genreconfig)
            genreroot = genretree.getroot()
            expr = "//genre[@name='%s' and @display-frontend='true']/@prose" % (rawgenre[0])
            self.genre = genreroot.xpath(expr)[0]

    def __construct_pages(self, root):
        pages = root.body.xpath("//division[@type='page']")
        self.pages = _get_pages(pages)

    def __extract_header_img(self, root):
        first_img = root.body.find('division').find('image')
        if (first_img.get('layout') == 'zmo_header'):
            self.header_img = Img(first_img)


@implementer(interfaces.IPage)
class Page(object):
    __content = []

    def __init__(self, page_xml):
        self.__content = iter(self._extract_items(page_xml))

    def __iter__(self):
        return self.__content

    def _extract_items(self, page_xml):
        content = []
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
        return content


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
    for page in pages_xml:
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
