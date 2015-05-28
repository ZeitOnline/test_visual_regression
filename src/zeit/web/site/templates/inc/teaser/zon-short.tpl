{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}
{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-short{% endblock %}
{% block teaser_time %}
   XXXXXXTIME XXXX {{ cp.include_teaser_datetime(teaser, self.layout()) }}
{% endblock %}
{% block teaser_product %}
   ZEI
{% endblock teaser_product %}

{% block teaser_media_position_before_title %}
{% endblock %}
{% block teaser_container %}
{% endblock %}
