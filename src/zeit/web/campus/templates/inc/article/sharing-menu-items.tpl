{% import 'zeit.web.campus:templates/macros/layout_macro.tpl' as lama %}
{% extends "zeit.web.core:templates/inc/article/sharing-menu-items.tpl" %}

{% block product %}
    ZEIT Campus
{% endblock %}

{% block fb_icon %}
    {{ lama.use_svg_icon('facebook', 'sharing-menu__icon', view.package) }}
{% endblock %}

{% block twitter_icon %}
    {{ lama.use_svg_icon('zco-twitter', 'sharing-menu__icon', view.package) }}
{% endblock %}

{% block wa_icon %}
    {{ lama.use_svg_icon('zco-wa', 'sharing-menu__icon', view.package) }}
{% endblock %}
