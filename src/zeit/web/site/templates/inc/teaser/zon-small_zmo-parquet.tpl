{% extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" %}

{% block teaser_kicker %}
    {% set is_zmo_parquet = area.referenced_cp and provides(area.referenced_cp, 'zeit.magazin.interfaces.IZMOContent') %}
    <span class="{{ '%s__kicker' | format(self.layout()) | with_mods(journalistic_format, 'zmo-parquet') }}">
        {{- teaser.teaserSupertitle or teaser.supertitle -}}
    </span>
    {%- if teaser.teaserSupertitle or teaser.supertitle -%}
        <span class="visually-hidden">:</span>
    {% endif %}
{% endblock %}
