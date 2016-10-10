{%- extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" -%}

{% block zplus_data %}{% endblock %}

{% block teaser_kicker %}
    <span class="{{ '%s__kicker' | format(self.layout()) | with_mods(journalistic_format, area.kind, 'zmo' if teaser is zmo_content, 'zett' if teaser is zett_content, 'zco' if teaser is zco_content) }}">
    {{ super() }}
{% endblock %}

{% block zplus_kicker_logo %}{% endblock %}
