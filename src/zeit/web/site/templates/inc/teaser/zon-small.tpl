{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser--small teaser--smallmedia teaser--hasmedia{% endblock %}
{% block teaser_heading_modifier %}teaser__heading__small{% endblock %}

{% block teaser_media_position_a %}
<figure class="teaser__media teaser__media--small" data-showimagemobile="true">
    <a class="teaser__media-link" title="Ukraine – Genscher für Ende der Russland-Sanktionen" href="http://www.zeit.de/politik/2014-09/hand-dietrich-genscher-putin-russland-ukraine">
        <img class="teaser__media-item teaser__media-item--small" alt="Genscher für Ende der Russland-Sanktionen" src="/img/demo/genscher-ukraine-540x304.jpg">
    </a>
    </figure>
{% endblock %}
