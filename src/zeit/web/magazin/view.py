import zeit.magazin.interfaces


def is_zmo_content(context, request):
    return zeit.magazin.interfaces.IZMOContent.providedBy(context)


def is_advertorial(context, request):
    return getattr(context, 'product_text', None) == 'Advertorial'
