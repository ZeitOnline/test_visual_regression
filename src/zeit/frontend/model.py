from lxml import objectify, etree
from os.path import isdir
from os.path import isfile
from zope.interface import implementer
from zeit.frontend import interfaces
import pkg_resources


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
	lead_pic = ''
	author = ''

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
		self.teaser_title = unicode(article_tree.getroot().teaser.title)
		self.teaser_text = unicode(article_tree.getroot().teaser.text)
		# Startbild
		# Datum | Uhrzeit
		# Autor
		# intertitle
		# division -> p | img -> bu

	def __construct_pages(self, root):
		pages = root.body.xpath("//division[@type='page']")
		self.pages = _get_pages(pages)


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
			if item.tag == 'image':
				content.append(Img(item))
			if item.tag == 'citation':
				content.append(Citation(item))
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


@implementer(interfaces.IVideo)
class Video(object):
	def __init__(self, xml):
		pass


def _get_pages(pages_xml):
	pages = []
	for page in pages_xml:
		pages.append(Page(page))
	return pages


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
