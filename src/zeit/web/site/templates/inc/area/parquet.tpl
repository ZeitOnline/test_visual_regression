{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% block before_module_list %}
<div class="parquet-row">
    <div class="parquet-meta">
        {% if area.referenced_cp is none %}
            <span class="parquet-meta__title">
                {{ area.title | hide_none }}
            </span>
        {% else %}
            <a class="parquet-meta__title" href="{{ area.referenced_cp.uniqueId | create_url }}">
                {{ area.title | hide_none }}
            </a>
            <ul class="parquet-meta__topic-links">
                {% for label, link in area.referenced_cp | topic_links %}
                    <li>
                        <a href="{{ link }}" class="parquet-meta__topic-link">
                            {{ label }}
                        </a>
                    </li>
                {% endfor %}
            </ul>
        {% endif %}

        {% if area.read_more and area.read_more_url %}
            <a href="{{ area.read_more_url }}" class="parquet-meta__more-link">
                {{ area.read_more }}
            </a>
        {% endif %}
    </div>
    <div class="parquet-teasers">
    {# XXX Do we really need the parquet-row and parquet-teasers divs? (ND) #}
{% endblock %}

{% block after_module_list %}
    </div>
</div>
{% endblock %}
