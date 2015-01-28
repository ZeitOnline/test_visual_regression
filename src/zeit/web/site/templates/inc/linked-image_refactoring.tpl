{%- extends "zeit.web.site:templates/inc/image_refactoring.tpl" -%}

{% if href %}
{% block mediablock_wrapper %}
<a class="{% block mediablock_link %}{% endblock %}" title="{{ image.attr_title | default('') }}" href="{{ href }}">
    {{ super() }}
</a>
{% endblock %}
{% endif %}
