{%- extends "zeit.web.site:templates/inc/teaser/zon-square.tpl" -%}

{% block teaser_modifier %}{{ self.layout() }}--zmo{% endblock %}

{% block teaser_container %}
    <div class="teaser-square__product">
        {{ lama.use_svg_icon('logo-zmo', 'teaser-square__zmo-logo', view.request) }}
    </div>
{% endblock %}
