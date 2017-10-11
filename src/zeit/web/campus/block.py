import grokcore.component
import zeit.campus.interfaces
import zeit.web
import zeit.web.core.block
import zeit.web.core.interfaces


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.campus.interfaces.IStudyCourse)
class StudyCourse(zeit.web.core.block.Block):

    def __new__(cls, context):
        if context.course is None:
            return None
        return super(StudyCourse, cls).__new__(cls, context)

    @zeit.web.reify
    def content(self):
        return self.context.course

    @zeit.web.reify
    def text(self):
        return self.content.text

    @zeit.web.reify
    def href(self):
        return self.content.href

    @zeit.web.reify
    def button_text(self):
        return self.content.button_text
