{% import 'zeit.web.campus:templates/macros/layout_macro.tpl' as lama %}
{% extends "zeit.web.core:templates/inc/article/sharing-menu-items.tpl" %}

{% block publisher %}ZEIT Campus ONLINE{% endblock %}

{% block fb_icon %}
    {{ lama.use_svg_icon('sharing-facebook', 'sharing-menu__icon', view.package) }}
{% endblock %}

{% block twitter_icon %}
    {{ lama.use_svg_icon('sharing-twitter', 'sharing-menu__icon', view.package) }}
{% endblock %}

{% block wa_icon %}
    {{ lama.use_svg_icon('sharing-whatsapp', 'sharing-menu__icon', view.package) }}
{% endblock %}

{% block mail %}{% endblock %}
