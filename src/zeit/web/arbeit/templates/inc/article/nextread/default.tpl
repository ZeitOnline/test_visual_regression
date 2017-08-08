{%- extends "zeit.web.arbeit:templates/inc/teaser/default.tpl" -%}

{% block layout %}nextread{% endblock %}

{% block teaser_text %}{% endblock%}
{% block teaser_commentcount %}{% endblock%}

{# not needed. and, btw, uses "area" which is not available on articles #}
{% block teaser_datetime %}{% endblock%}
{% block meetrics %}{% endblock%}

{% block teaser_media %}
    {% require image = get_image(module, fallback=False, variant_id="wide") -%}
        {% set module_layout = self.layout() %}
        {% set href = teaser | create_url %}
        {% set media_caption_additional_class = 'figcaption--hidden' %}
        {% include "zeit.web.core:templates/inc/asset/image_linked.tpl" %}
    {% endrequire %}
{% endblock %}

{% block teaser_label -%}
    <div class="{{ self.layout() }}__lead">{{ module.lead or 'Lesen Sie jetzt' }}</div>
{%- endblock %}

{% block teaser_title %}
    <span class="{{ self.layout() }}__title">
        <span class="{{ self.layout() }}__title--underlined">{{ teaser.teaserTitle or teaser.title }}</span>
    </span>
{% endblock %}
