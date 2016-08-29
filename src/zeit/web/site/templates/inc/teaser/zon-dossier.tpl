{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-dossier{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/asset/image_zon-dossier.tpl" ignore missing %}
    <div class="teaser-dossier__marker">Dossier</div>
{% endblock %}

{% block teaser_journalistic_format %}{% endblock %}
