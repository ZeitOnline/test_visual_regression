import grokcore.component

import zeit.content.author.interfaces

import zeit.web.core.interfaces
import zeit.web.core.centerpage


@grokcore.component.implementer(zeit.web.core.interfaces.ITopicLink)
@grokcore.component.adapter(zeit.content.author.interfaces.IAuthor)
class AuthorTopicLink(zeit.web.core.centerpage.TopicLink):
    pass
