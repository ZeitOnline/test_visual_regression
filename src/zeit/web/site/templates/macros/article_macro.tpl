{% extends 'zeit.web.core:templates/macros/article_macro.tpl' %}
{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% import 'zeit.web.site:templates/macros/video_macro.tpl' as vima %}

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
