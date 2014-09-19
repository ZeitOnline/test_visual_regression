import zeit.magazin.interfaces


def is_zmo_content(context, request):
    return zeit.magazin.interfaces.IZMOContent.providedBy(context)
