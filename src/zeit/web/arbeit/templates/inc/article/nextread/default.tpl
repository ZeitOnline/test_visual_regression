{%- extends "zeit.web.arbeit:templates/inc/teaser/default.tpl" -%}

{% block layout %}nextread{% endblock %}

{% block teaser_text %}{% endblock%}
{% block teaser_commentcount %}{% endblock%}

{#- not needed. and, btw, uses "area" which is not available on articles -#}
{% block teaser_datetime %}</div>{% endblock%} {#- closes .nextread__wrapper -#}
{% block meetrics %}{% endblock%}

{%- block teaser_additional_attribute_for_textlink %} data-id="articlebottom.editorial-nextread...text"{% endblock %}

{% block teaser_media %}
    <div class="nextread__wrapper"> {#- needed to apply display: table -#}
    {% require image = get_image(module, fallback=False, variant_id="wide") -%}
        {% set module_layout = self.layout() %}
        {% set href = teaser | create_url %}
        {% set media_caption_additional_class = 'figcaption--hidden' %}
        {% set tracking_slug = "articlebottom.editorial-nextread..." %}
        {% include "zeit.web.core:templates/inc/asset/image_linked.tpl" %}
    {% endrequire %}
{% endblock %}

{% block teaser_label -%}
    <div class="{{ self.layout() }}__lead">{{ module.lead or 'Lesen Sie jetzt:' }}</div>
{%- endblock %}

{% block teaser_title %}
    <span class="{{ self.layout() }}__title">
        <span class="{{ '%s' | format (self.layout() ~ '__title') | with_mods('underlined' if view.is_advertorial else 'underlined-skip') }}">{{ teaser.teaserTitle or teaser.title }}</span>
    </span>
{% endblock %}
