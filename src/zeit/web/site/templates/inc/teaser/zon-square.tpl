{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-square{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}.tpl".format(teaser | auto_select_asset | block_type)
        ignore missing with context %}
{% endblock %}

{% block teaser_container %}
    <div class="teaser-square__product">
        <div class="teaser-square__zmo-logo icon-logo-zmo-large"></div>
    </div>
{% endblock %}
