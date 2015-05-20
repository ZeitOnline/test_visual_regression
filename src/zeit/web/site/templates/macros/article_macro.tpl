{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama_core with context %}
{% extends 'zeit.web.core:templates/macros/article_macro.tpl' %}

{% macro image(obj, loop) -%}
    {% if obj | default_image_url -%}
        <figure class="
            {%- if loop -%}
                slide
            {%- elif obj.layout == 'large' -%}
                article__item article__item--wide
            {%- elif obj.layout == 'small' -%}
                article__item article__item--marginalia
            {%- endif -%}
            ">
            <div class="scaled-image">
                {{ lama_core.insert_responsive_image(obj, None, 'article') }}
            </div>
            <figcaption class="figure__caption {% if obj.layout == 'small' %}figure__caption--marginalia{%- endif -%}">
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

{% macro intertitle(intertitle) -%}
    <h2 class="article__subheading article__item">
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
        {{ html|safe }}
    </p>
{%- endmacro %}

{% macro place(item) -%}
    {{ lama_core.adplace(item, view) }}
    {{ lama_core.adplace_middle_mobile(item) }}
{%- endmacro %}

{% macro contentadblock(item) -%}
{#
    {{ lama_core.content_ad_article(view) }}
#}
{%- endmacro %}

{% macro portraitbox(obj) -%}
  {#
    obj = {'name': u'Kai Biermann',
           'text': (u'<p>Kai Biermann ist Redakteur im Team Investigativ/Daten bei '
                    u'ZEIT&nbsp;ONLINE. Seine Profilseite finden Sie '
                    u'<a href="http://community.zeit.de/user/kai-biermann">hier</a>.</p>')
           }
  #}
    {% if obj.name -%}
        <figure class="portraitbox article__item article__item--marginalia">
            <div class="portraitbox__heading">
                {{ obj.name }}
            </div>
            <div class="portraitbox__body">
                {{ obj.text | safe }}
            </div>
        </figure>
    {%- endif %}
{%- endmacro %}

{% macro infobox(obj) %}
{% if obj.contents -%}
    {% set id = obj.title | attr_safe %}
    <aside class="infobox js-infobox" id="{{ id }}" role="application">
        <div class="infobox__navigation" id="{{ id }}--navigation" role="tablist"></div>
        <div class="infobox__content">
            {% for title, text in obj.contents %}
                <section class="infobox-tab" id="{{ id }}-{{ loop.index }}">
                    <h3
                        data-role="tab"
                        data-aria-controls="{{ id }}-{{ loop.index }}-article"
                        class="infobox-tab__title"
                        data-index="{{ loop.index }}"
                        tabindex="0">
                        <a tabindex="-1" class="infobox-tab__link" href="#{{ id }}-{{ loop.index }}">{{ title }}</a>
                    </h3>
                    <article
                        role="tabpanel"
                        aria-labelledby="{{ id }}-{{ loop.index }}-tab"
                        class="infobox-tab__content"
                        id="{{ id }}-{{ loop.index }}-article">
                        {% for item in text %}
                            {{ (item | block_type or "no_block") | macro(item) }}
                        {% endfor %}
                    </article>
                </section>
            {% endfor %}
        </div>
    </aside>
{%- endif %}
{%- endmacro %}
