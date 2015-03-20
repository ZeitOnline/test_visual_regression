{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama_core with context %}
{% extends 'zeit.web.core:templates/macros/article_macro.tpl' %}

{% macro image(obj, loop) -%}
    {% if obj | default_image_url -%}
        <figure class="
            {%- if loop -%}
                slide
            {%- elif obj.layout == 'large' -%}
                article__item article__item--wide
            {%- endif -%}
            ">
            <div class="scaled-image">
                {{ insert_responsive_image(obj, None, 'article') }}
            </div>
            <figcaption class="figure__caption">
                {% if loop -%}
                <span class="figure__index">{{ loop.index }}/{{ loop.length }}</span>
                {% endif -%}
                <span class="figure__text">{{ obj.caption|hide_none }}</span>
                {% if obj.copyright|count and obj.copyright[0][0] != '©' %}
                <span class="figure__copyright">
                    {%- if obj.copyright[0][1] -%}
                    <a href="{{ obj.copyright[0][1] }}" target="_blank">
                    {%- endif -%}
                        {{ obj.copyright[0][0] }}
                    {%- if obj.copyright[0][1] -%}
                    </a>
                    {%- endif -%}
                </span>
                {% endif %}
            </figcaption>
        </figure>
    {%- endif %}
{%- endmacro %}

{% macro insert_responsive_image(image, image_class, page_type) %}

    {% set alt = ''%}
    {% set title = ''%}

    {% if image.alt %}
        {% set alt = image.alt %}
        {% set title = image.title %}
    {% elif image.attr_alt %}
        {% set alt = image.attr_alt %}
        {% set title = image.attr_title %}
    {% endif %}

    {% if image %}
        <!--[if gt IE 8]><!-->
            <noscript data-src="{{image | default_image_url}}">
        <!--<![endif]-->
        {% if page_type == 'article' and image.href %}
            <a href="{{image.href}}">
        {% endif %}
                <img alt="{{alt}}" {% if title %}title="{{title}}" {% endif %}class="{{image_class | default('', true)}} figure__media" src="{{image | default_image_url}}" data-ratio="{{image.ratio}}">
        {% if page_type == 'article' and image.href %}
            </a>
        {% endif %}
        <!--[if gt IE 8]><!-->
            </noscript>
        <!--<![endif]-->
    {% endif %}
{% endmacro %}

{% macro intertitle(intertitle) -%}
    <h2 class="article__subheading">
        {{ intertitle|striptags }}
    </h2>
{%- endmacro %}

{% macro paragraph(html, class) -%}
  {#
    html = (u'Sieben Begriffe für ein und denselben <i>Gegenstand</i> – das ist '
            u'deutsches Kulturgut. <b>Dialekte</b> gehören schon immer zu diesem '
            u'viel durchwanderten und umkämpften Land. Auch die deutsche '
            u'Teilung hat zur <a href="#">sprachlichen Vielfalt</a> beigetragen.')
  #}
    <p class="paragraph article__item">
        {{ html | safe}}
    </p>
{%- endmacro %}

{% macro place(item) -%}
{#
    {{ lama_core.adplace(item, view) }}
    {{ lama_core.adplace_middle_mobile(item) }}
#}
{%- endmacro %}

{% macro portraitbox(obj) -%}
  {#
    obj = {'name': u'Herrmann Koser',
           'text': (u'Herrmann Koser ist ZEITmagazin-Leserin und eine der '
                    u'meinungsstarken Kommentatoren bei unseren sonntäglichen '
                    u'Tatort-Diskussionen bei Facebook.')
           }
  #}
    {% if obj.name -%}
        <figure class="portraitbox figure-stamp">
            <div class="portraitbox-heading">
                {{ obj.name }}
            </div>
            {{ obj.text | safe }}
        </figure>
    {%- endif %}
{%- endmacro %}
