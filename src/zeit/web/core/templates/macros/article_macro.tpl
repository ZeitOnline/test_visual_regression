{% macro meta_author(authors, class="article__head__meta__author", titlecase=True) %}
    {%- if authors -%}
        {%- for author in authors -%}
            {%- if titlecase -%}
                {{ author.prefix|title }}
            {% else %}
                {{ author.prefix }}
            {% endif %}
            {%- if author.href -%}
                <a href="{{ author.href|translate_url }}" class="{{ class }}" itemprop="url"><span itemprop="name">{{ author.name }}</span></a>{{ author.location }}
            {%- else -%}
                <span class="{{ class }}"><span itemprop="name">{{ author.name }}</span>{{ author.location }}</span>
            {%- endif -%}
            {{ author.suffix }}
        {%- endfor -%}
    {%- endif -%}
{% endmacro %}

{% macro inlinegallery(obj, wrapper_class='inline-gallery__wrap') -%}
    <div class="{{ wrapper_class }}">
        <div class="inline-gallery">
            {% for entry in obj.itervalues() -%}
                {{ image(entry, loop) }}
            {%- endfor %}
        </div>
    </div>
{%- endmacro %}

{% macro no_block(obj) %}{% endmacro %}
