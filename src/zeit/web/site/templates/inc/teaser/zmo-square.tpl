{%- extends "zeit.web.site:templates/inc/teaser/zon-square.tpl" -%}

{% block teaser_modifier %}{{ self.layout() }}--zmo{% endblock %}

{% block teaser_container %}
    <div class="teaser-square__product">
        <div class="teaser-square__zmo-logo icon-logo-zmo-large"></div>
    </div>
{% endblock %}
