{% extends 'zeit.web.core:templates/macros/article_macro.tpl' %}
{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% import 'zeit.web.site:templates/macros/video_macro.tpl' as vima %}

{% macro infobox(obj) -%}
    {% if obj.contents -%}
    {% set id = obj.title | attr_safe %}
    <aside class="infobox js-infobox" id="{{ id }}" role="application">
        <div class="infobox__container">
            <div class="infobox__navigation"></div>
            <div class="infobox__content">
            {% for title, text in obj.contents %}
                <section class="infobox-tab" id="{{ id }}-{{ loop.index }}">
                    <h3 class="infobox-tab__title" role="presentation">
                        <a
                            class="infobox-tab__link"
                            id="{{ id }}-{{ loop.index }}-tab"
                            role="tab"
                            href="#{{ id }}-{{ loop.index }}"
                            data-id="{{ id }}-{{ loop.index }}-tab"
                            aria-controls="{{ id }}-{{ loop.index }}-article">
                            {{- title -}}
                        </a>
                    </h3>
                    <article
                        class="infobox-tab__panel"
                        id="{{ id }}-{{ loop.index }}-article"
                        role="tabpanel"
                        aria-labelledby="{{ id }}-{{ loop.index }}-tab">
                        {% for item in text %}
                            {{ (item | block_type or "no_block") | macro(item) }}
                        {% endfor %}
                    </article>
                </section>
            {% endfor %}
            </div>
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
    {% set static_param = '' %}
    {% include 'zeit.web.site:templates/inc/module/cardstack.html' %}
{% endmacro -%}

{# Quiz macro is used inside of articles. (On CPs, the module template is used.) #}
{% macro quiz(module) -%}
    <div class="article__item article__item--wide article__item--rimless x-spacing">
        <iframe frameborder="0" scrolling="no" width="100%" height="480" src="{{ module.url }}?embedded{{ module.adreload }}"></iframe>
    </div>
{% endmacro -%}

{% macro video(video) -%}
    <div class="article__item article__item--wide article__item--rimless article__item--apart">
        {% set playerId = 'c09a3b98-8829-47a5-b93b-c3cca8a4b5e9' %}
        {{ vima.brightcove_video_tag(video.id, iframe=True, brightcove_player=playerId) }}
        <figcaption class="video-figure__caption">
            <span class="video-figure__pagetitle">{{ [video.supertitle, video.title] | join_if_exists(' - ') }}</span>
            <span class="video-figure__description">{{ video.description }}</span>
        </figcaption>
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
