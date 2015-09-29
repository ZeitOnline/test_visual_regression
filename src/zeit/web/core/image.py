from datetime import datetime

import pytz

import zeit.cms.workflow.interfaces
import zeit.content.image.interfaces

import zeit.web


# XXX Should this be a method of Image/ImageGroup?
def image_expires(image):
    """Returns number of seconds relative to now when the given image, or the
    image group it belongs to, will no longer be published.
    """
    if zeit.content.image.interfaces.IImage.providedBy(image):
        group = image.__parent__
    else:
        group = image
    if not zeit.content.image.interfaces.IImageGroup.providedBy(group):
        return None

    workflow = zeit.cms.workflow.interfaces.IPublishInfo(group)
    if workflow.released_to:
        now = datetime.now(pytz.UTC)
        return int((workflow.released_to - now).total_seconds())


@zeit.web.register_global
def is_image_expired(image):
    expires = image_expires(image)
    if expires is None:
        return False
    return (expires < 0)
