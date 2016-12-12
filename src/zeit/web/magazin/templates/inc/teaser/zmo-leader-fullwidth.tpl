{#
Teaser template for fullwidth lead teaser
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}
{% block teaser_kicker %}{% endblock %}
{% block comments %}{% endblock %}

{% block teaser_title %}
    {% if teaser is zplus_content %}
        {{ lama.use_svg_icon('zplus', 'zplus-logo zplus-logo--s svg-symbol--hide-ie', view.package, a11y=False) }}
    {% endif %}
    {{ super() }}
{% endblock teaser_title%}


{% block teaser_image scoped %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.magazin:templates/inc/asset/image-fullwidth.tpl" %}
{% endblock %}
