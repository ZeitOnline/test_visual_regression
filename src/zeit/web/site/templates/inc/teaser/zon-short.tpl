{% extends "zeit.web.site:templates/inc/teaser/default.tpl" %}

{% block layout %}teaser-short{% endblock %}
{% block meetrics %}{% endblock %}
{% block teaser_time %}
   {{ cp.include_teaser_time(teaser, self.layout()) }}
{% endblock %}
{% block teaser_product %}
   <span class="teaser-short__product">{{ teaser.product.id }}</span>
{% endblock teaser_product %}

{% block teaser_container %}
{% endblock %}
