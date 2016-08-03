{% extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" %}

{% block teaser_kicker %}
    <span class="{{ '%s__kicker' | format(self.layout()) | with_mods('zett-parquet') }}">
        {{- teaser.teaserSupertitle or teaser.supertitle -}}
    </span>
    {%- if teaser.teaserSupertitle or teaser.supertitle -%}
        <span class="visually-hidden">:</span>
    {% endif %}
{% endblock %}

{% block teaser_label %}
    {% if module[0].is_ad %}
        <span class="{{ self.layout() }}__label">Anzeige</span>
    {% endif %}
{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {# forces mobile image for first zett teaser #}
    {% if loop.index == 1 and module[0].is_ad == False %}
        {% set force_mobile_image = True %}
    {% endif %}
    {% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" ignore missing %}
{% endblock %}



