import grokcore.component
import zeit.campus.interfaces
import zeit.web.core.block
import zeit.web.core.interfaces


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.campus.interfaces.IStudyCourse)
class StudyCourse(zeit.web.core.block.Block):

    def __new__(cls, context):
        if context.course is None:
            return None
        return super(StudyCourse, cls).__new__(cls, context)

    def __init__(self, model_block):
        self.model_block = model_block

    @property
    def text(self):
        return self.model_block.course.text

    @property
    def href(self):
        return self.model_block.course.href

    @property
    def button_text(self):
        return self.model_block.course.button_text
