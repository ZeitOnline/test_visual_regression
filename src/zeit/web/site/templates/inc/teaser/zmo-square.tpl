{%- extends "zeit.web.site:templates/inc/teaser/zon-square.tpl" -%}

{% block teaser_modifier %}{{ self.layout() }}--zmo{% endblock %}

{% block kicker_logo %}
    {% set logo_layout = self.layout() %}
    {% for template in teaser | logo_icon(area.kind, zplus='only') %}
        {% include "zeit.web.core:templates/inc/badges/{}.tpl".format(template) %}
    {% endfor %}
{% endblock %}

{% block teaser_container %}
    <div class="teaser-square__product">
        {{ lama.use_svg_icon('logo-zmo', 'teaser-square__zmo-logo', view.package) }}
    </div>
{% endblock %}
