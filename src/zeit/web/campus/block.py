import grokcore.component
import zeit.campus.interfaces
import zeit.web.core.block
import zeit.web.core.interfaces


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.campus.interfaces.IStudyCourse)
class StudyCourse(zeit.web.core.block.Block):

    def __init__(self, model_block):
        self.text = model_block.course.text
        self.href = model_block.course.href
        self.button_text = model_block.course.button_text
