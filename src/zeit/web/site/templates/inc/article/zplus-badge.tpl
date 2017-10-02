{%- extends "zeit.web.site:templates/inc/article/zplus-badge-base.tpl" -%}

{% block volumeteaser %}
{% if view.volumepage_is_published %}
    <a class="{{ self.layout() }}__link" href="{{ view.zplus_label.link }}">
        {{ super() }}
    </a>
{% else %}
    {{ super() }}
{% endif %}
{% endblock volumeteaser %}
