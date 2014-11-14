{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "-teaser-fullwidth.tpl" ignore missing with context %}
    <div class="{{ self.layout() }}__inner-helper">
{% endblock %}

{% block teaser_media_position_after_container %}
    </div>
{% endblock %}
