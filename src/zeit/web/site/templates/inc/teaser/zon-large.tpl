{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser--hasmedia{% endblock %}
{% block teaser_heading_modifier %}teaser__heading--hasmedia{% endblock %}

{% block teaser_media_position_b %}    
    {# Create include statement    
    {% include view.teaser_media(teaser) ignore missing with context %}
    #} 
    <figure class="teaser__media">
        <a class="teaser__media-link" title="Olympische Spiele 2024 - Deutsche wünschen sich gemeinsame Bewerbung von Berlin und Hamburg" href="http://www.zeit.de/sport/2014-09/umfrage-olympische-spiele-berlin-hamburg">
            <img class="teaser__media-item" alt="Olympische Spiele 2024 - Deutsche wünschen sich gemeinsame Bewerbung von Berlin und Hamburg" src="/img/demo/olympische-spiele-540x304.jpg">
        </a>
    </figure>
{% endblock %}
