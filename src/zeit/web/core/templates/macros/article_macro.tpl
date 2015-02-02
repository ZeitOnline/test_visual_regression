{% macro meta_author(authors, class="article__head__meta__author", titlecase=True) %}
    {%- if authors -%}
        {%- for author in authors -%}
            {%- if titlecase -%}
                {{ author.prefix|title }}
            {% else %}
                {{ author.prefix }}
            {% endif %}
            {%- if author.href -%}
                <a href="{{ author.href|translate_url }}" class="{{ class }}">{{ author.name }}</a>{{ author.location }}
            {%- else -%}
                <span class="{{ class }}">{{ author.name }}{{ author.location }}</span>
            {%- endif -%}
            {{ author.suffix }}
        {%- endfor -%}
    {%- endif -%}
{% endmacro %}

{% macro no_block(obj) %}{% endmacro %}
