{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{% macro subpage_index(pages, subtitle, number, index_class, active_class) -%}
    {% if subtitle %}
    <div class="{{ index_class }} figure-stamp">
        <div class="article__subpage-index__title">&uuml;bersicht</div>
        <ol>
            {% for page in pages if page.teaser %}
                <li class="article__subpage-index__item">
                    <span class="article__subpage-index__item__count">{{ page.number }} &mdash; </span>
                    <span class="article__subpage-index__item__title-wrap">
                        {% if loop.index == number %}
                            <span class="article__subpage-index__item__title {{ active_class }}">{{ page.teaser }}</span>
                        {% else %}
                            <a href="#kapitel{{ loop.index }}" class="article__subpage-index__item__title js-scroll">{{ page.teaser }}</a>
                        {% endif %}
                    </span>
                </li>
            {% endfor %}
        </ol>
    </div>
    {% endif %}
{%- endmacro %}

{% macro subpage_head(number, subtitle, class) -%}
    {% if subtitle %}
        <div class="{{ class }}" id="kapitel{{ number }}">
            {{- number }} &mdash; {{ subtitle -}}
        </div>
    {% endif %}
{%- endmacro %}

{% macro video(obj) -%}
    {% if obj.id and 'header' not in obj.format | default('') -%}
        <figure class="
        {% if obj.format == 'zmo-small-left' or obj.format == 'small' %}
            figure-stamp
        {% elif obj.format == 'large' or obj.format == 'zmo-large-left' or obj.format == 'zmo-large-center' or obj.format == 'zmo-large-right' %}
            figure-full-width
        {% elif obj.format == 'zmo-small-right' %}
             figure-stamp--right
        {% else %}
             figure is-constrained is-centered
        {% endif %}" data-video="{{ obj.id }}">
            <div class="video__still">
                <img class="figure__media" src="{{ obj.video_still| default('http://placehold.it/160x90', true) }}" alt="Video: {{ obj.title }}" title="Video: {{ obj.title }}">
                <span class="video__button">{{ lama.use_svg_icon('playbutton', 'video__play-icon', view.package) }}</span>
            </div>
            <figcaption class="figure__caption">
                    {{ obj.description }}
            </figcaption>
        </figure>
    {%- endif %}
{%- endmacro %}

{% macro headervideo(obj, wrap_class='article__main-video--longform', img_class='') -%}

    {% if obj.id is not defined and obj.uniqueId -%}
        {% set id = obj.uniqueId | substring_from('/') %}
    {% elif obj.id -%}
        {% set id = obj.id %}
    {% endif %}

    {% if id %}
        <div data-backgroundvideo="{{ id }}" class="{{ wrap_class }}">
            <video preload="auto" loop="loop" muted="muted" volume="0" poster="{{ obj.video_still }}">
                <source src="{{ obj.highest_rendition }}" type="video/mp4">
                <source src="http://live0.zeit.de/multimedia/videos/{{ id }}.webm" type="video/webm">
            </video>
            <img class="video--fallback {{ img_class }}" src="http://live0.zeit.de/multimedia/videos/{{ id }}.jpg" alt="Video: {{ obj.title }}" title="Video: {{ obj.title }}">
        </div>
    {% endif %}
{%- endmacro %}

{% macro add_publish_date( lm_date, publish_date, format) -%}
    {% if lm_date %}
        <!--[if gt IE 8]><!-->
        <script type="text/javascript">
        // due to seo reasons, original publish date is added later
            var time = document.querySelector('.article__head__meta__date'),
                content = time.textContent != undefined ? time.textContent : time.innerText,
                published = document.createTextNode('{{ publish_date }} — '),
                linebreak = document.createElement('br'),
                text = "{% if format == 'long' %}zuletzt aktualisiert am {% else %}editiert: {% endif %}" + content;

            if ( content != undefined ) {
                time.parentNode.insertBefore(published, time);
                time.parentNode.insertBefore(linebreak, time);
                time.firstChild.nodeValue = text;
            }
        </script>
        <!--<![endif]-->
    {% endif %}
{%- endmacro %}
