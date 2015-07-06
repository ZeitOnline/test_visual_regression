{%- extends "zeit.web.site:templates/inc/teaser/zon-large_blog.tpl" -%}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
{% endblock %}

{% block teaser_media_position_after_title %}
{% endblock %}
