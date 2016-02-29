{% extends 'zeit.web.core:templates/macros/article_macro.tpl' %}
{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% import 'zeit.web.site:templates/macros/video_macro.tpl' as vima %}

{% macro citation(obj) -%}
    <figure class="quote article__item">
        <blockquote class="quote__text">
            {{ obj.text }}
        </blockquote>
        {% if obj.attribution %}
            <figcaption class="quote__source">
                {% if obj.url %}
                    <a class="quote__link" href="{{ obj.url }}">
                        {{ obj.attribution }}
                    </a>
                {% else %}
                    {{ obj.attribution }}
                {% endif %}
            </figcaption>
        {% endif %}
    </figure>
{%- endmacro %}
