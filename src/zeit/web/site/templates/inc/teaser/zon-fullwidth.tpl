{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
    <div class="{{ self.layout() }}__inner-helper">
{% endblock %}

{% block teaser_media_position_after_container %}
    </div>
{% endblock %}
