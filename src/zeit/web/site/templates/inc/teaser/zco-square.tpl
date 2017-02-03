{%- extends "zeit.web.site:templates/inc/teaser/zon-square.tpl" -%}

{% block teaser_modifier %}{{ self.layout() }}--zco{% endblock %}

{% block kicker_logo %}
    {% set logo_layout = self.layout() %}
    {% for template in teaser | logo_icon(area.kind, zplus_only=True) %}
        {% include "zeit.web.core:templates/inc/badges/{}.tpl".format(template) %}
    {% endfor %}
{% endblock %}

{% block teaser_container %}
    <div class="teaser-square__product">
        {{ lama.use_svg_icon('logo-zco', 'teaser-square__zco-logo', 'zeit.web.campus') }}
    </div>
{% endblock %}
