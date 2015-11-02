{% extends 'zeit.web.core:templates/macros/article_macro.tpl' %}
{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% import 'zeit.web.site:templates/macros/video_macro.tpl' as vima %}

{% macro image(image, loop) -%}
    {% include 'zeit.web.site:templates/inc/asset/image_article.tpl' with context %}
{%- endmacro %}

{% macro intertitle(intertitle) -%}
    <h2 class="article__subheading article__item">
        {{ intertitle | striptags }}
    </h2>
{%- endmacro %}

{% macro liveblog(liveblog, view) -%}
    {% if liveblog.blog_id -%}
        <div class="liveblog">
            {% set esi_source = 'http://www.zeit.de/liveblog-backend/{}.html'.format(liveblog.blog_id) %}
            {{ lama.insert_esi(esi_source, 'Liveblog konnte nicht geladen werden', view.is_dev_environment) }}
        </div>
    {%- endif %}
{%- endmacro %}

{% macro paragraph(html) -%}
  {#
    html = (u'Sieben Begriffe für ein und denselben <i>Gegenstand</i> – das ist '
            u'deutsches Kulturgut. <b>Dialekte</b> gehören schon immer zu diesem '
            u'viel durchwanderten und umkämpften Land. Auch die deutsche '
            u'Teilung hat zur <a href="#">sprachlichen Vielfalt</a> beigetragen.')
  #}
    <p class="paragraph article__item">
        {{ html | safe }}
    </p>
{%- endmacro %}

{% macro unorderedlist(html) -%}
  {#
    html = (u'<li>And I will <i>strike down</i> upon thee with <em>great vengeance</em></li>'
            u'<li>and <b>furious anger</b> those who <strong>would</strong> attempt</li>'
            u'<li>to poison and destroy <a href="#">My brothers</a>.</li>')
  #}
    <ul class="list article__item">
        {{ html | safe }}
    </ul>
{%- endmacro %}

{% macro orderedlist(html) -%}
  {#
    html = (u'<li>And I will <i>strike down</i> upon thee with <em>great vengeance</em></li>'
            u'<li>and <b>furious anger</b> those who <strong>would</strong> attempt</li>'
            u'<li>to poison and destroy <a href="#">My brothers</a>.</li>')
  #}
    <ol class="list article__item">
        {{ html | safe }}
    </ol>
{%- endmacro %}

{% macro place(item, view) -%}

    {# On "komplettansicht", we do not want to have duplicate banner IDs.
    That's why we set Banners 7+8+9 only on the first three pages and do
    not display ads on other pages. #}
    {% if view.is_all_pages_view %}
        {% if item.on_page_nr == 1 %}
            {{ lama.adplace(view.banner(7), view) }}
            {{ lama.adplace(view.banner(4), view, mobile=True) }}
        {% elif item.on_page_nr == 2 %}
            {{ lama.adplace(view.banner(9), view) }}
        {% endif %}
    {% else %}
        {{ lama.adplace(item, view) }}
        {% if item.tile == 7 %}
            {{ lama.adplace(view.banner(4), view, mobile=True) }}
        {% endif %}
    {% endif %}

{%- endmacro %}

{% macro contentadblock(item, view) -%}
    {{ lama.content_ad_article(view) }}
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

{% macro raw(obj) -%}
    {% if obj.alldevices %}
    <div class="raw">{{ obj.xml | safe }}</div>
    {% endif %}
{%- endmacro %}

{% macro cardstack(module, view) -%}
    {% set request = view.request %}
    {% include 'zeit.web.site:templates/inc/module/cardstack.html' %}
{% endmacro -%}

{% macro video(video) -%}
    <div class="article__item article__item--wide article__item--rimless article__item--apart">
        {% set playerId = 'c09a3b98-8829-47a5-b93b-c3cca8a4b5e9' %}
        {{ vima.brightcove_video_tag(video.id, iframe=True, brightcove_player=playerId) }}
    </div>
{% endmacro -%}

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
