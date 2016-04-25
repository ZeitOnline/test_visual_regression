{% import 'zeit.web.campus:templates/macros/layout_macro.tpl' as lama %}
{% extends "zeit.web.core:templates/inc/article/sharing-menu-items.tpl" %}

{% block fb_icon %}
    {{ lama.use_svg_icon('fb-40x40', 'sharing-menu__icon', view.package) }}
{% endblock %}

{% block twitter_icon %}
    {{ lama.use_svg_icon('twitter-40x40', 'sharing-menu__icon', view.package) }}
{% endblock %}

{% block wa_icon %}
    {{ lama.use_svg_icon('whatsapp-40x40', 'sharing-menu__icon', view.package) }}
{% endblock %}
