from lxml import etree
from zeit.frontend.model import Citation
from zeit.frontend.model import Img
from zeit.frontend.model import Intertitle
from zeit.frontend.model import Para

def mock_p():
    p = """
           <p>Text <a href='foo'> ba </a> und <em>Text</em>
           abc</p>
       """

    xml = etree.fromstring(p)
    return Para(xml)


def mock_img():
    p = """
           <image layout="" align="" src="">
                <bu>foo</bu><copyright>foo</copyright>
           </image>
       """

    xml = etree.fromstring(p)
    return Img(xml)


def mock_intertitle():
    it = """
        <intertitle>Foo</intertitle>
        """
    xml = etree.fromstring(it)
    return Intertitle(xml)


def mock_citation():
    cit = """
        <citation />
        """
    xml = etree.fromstring(cit)
    return Citation(xml)
