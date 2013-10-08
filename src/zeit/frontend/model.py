from lxml import objectify, etree
from os.path import isdir
from os.path import isfile
from pyramid.view import view_config
import pkg_resources

class Resource(object):
    pass


class Directory(Resource):
    base_path = ''

    def __init__(self, base_path):
        self.base_path = base_path

    def __getitem__(self, name):
        path=self.base_path+'/'+name
        if isdir(path):
            return Directory(path)
        if isfile(path):
            return Content(path)
        else:
            raise KeyError


def get_root(request):
    return Directory(pkg_resources.resource_filename(__name__,'data'))


class Content (Resource):
    title = 'foo'
    subtitle = 'baa'
    teaser_title = 'teaser_title'
    teaser_text = 'teaser_text'
    page = ''

    def __json__(self, request):
        return dict((name, getattr(self, name)) for name in dir(self) if not name.startswith('__')) 

    def __init__(self, path):
        article_tree = objectify.parse(path)
        self.title = unicode(article_tree.getroot().body.title)
        self.subtitle = unicode(article_tree.getroot().body.subtitle)
        self.page = etree.tostring(article_tree.getroot().body.xpath("//division[@type='page']")[0])
        self.teaser_title = unicode(article_tree.getroot().teaser.title)
        self.teaser_text = unicode(article_tree.getroot().teaser.text)


@view_config(route_name='json', context=Content,
             renderer='json')
@view_config(context=Content,
             renderer='templates/article.html')
def render_content(context, request):
    return {'article':context}

@view_config(route_name='json', context=Content,
             renderer='json', name='teaser')
@view_config(name='teaser', context=Content,
             renderer='templates/teaser.html')
def render_teaser(context, request):
    return {
            'teaser_title':context.teaser_title,
            'teaser_text': context.teaser_text,
            }




