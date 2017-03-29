{%- extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" -%}

{%- block kicker_class -%}{{ '%s__kicker' | format(self.layout()) | with_mods(journalistic_format, area.kind ) }}{% endblock %}

{% block zplus_data %}{% endblock %}

{% block content_kicker_logo %}{% endblock %}

{% block teaser_datetime %}{% endblock %}
