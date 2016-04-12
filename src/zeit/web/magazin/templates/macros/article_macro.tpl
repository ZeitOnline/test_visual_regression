{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{% macro place(item) -%}
    {{ lama.adplace(item, view) }}
    {{ lama.adplace_middle_mobile(item, view) }}
{%- endmacro %}

{% macro contentadblock(item) -%}
    {% include 'zeit.web.core:templates/inc/blocks/contentadblock.html' %}
{%- endmacro %}

{% macro supertitle() -%}
  <div class="article__head__supertitle">{{ view.supertitle }}</div>
{%- endmacro %}

{% macro title() -%}
  <div class="article__head__title">{{ view.title }}</div>
{%- endmacro %}

{% macro subtitle(include_meta=False, with_quotes=False) -%}
    <div class="article__head__subtitle">
        <p>
            <strong>
                {% if with_quotes %}
                    »{{ view.subtitle }}«
                {% else %}
                    {{ view.subtitle }}
                {% endif %}
                {% if include_meta and view.genre %}
                    {{ view.genre | title }}
                {% endif %}
                {% if include_meta and view.authors %}
                    {{ meta_author(view.authors, titlecase=view.genre==None) }}
                {% endif %}
            </strong>
        </p>
    </div>
{%- endmacro %}

{% macro liveblog(liveblog) -%}
    {% if liveblog.blog_id -%}
        <div class="is-constrained is-centered">
            {# TODO: We should mock the liveblog backend for local testing. #}
            {% set esi_source = 'http://www.zeit.de/liveblog-backend/{}.html'.format(liveblog.blog_id) %}
            {{ lama.insert_esi(esi_source, 'Liveblog konnte nicht geladen werden') }}
        </div>
    {%- endif %}
{%- endmacro %}

{% macro paragraph(html) -%}
    <p class="is-constrained is-centered">
        {{ html | safe}}
    </p>
{%- endmacro %}

{% macro unorderedlist(html) -%}
    <ul class="is-constrained is-centered">
        {{ html | safe }}
    </ul>
{%- endmacro %}

{% macro orderedlist(html) -%}
    <ol class="is-constrained is-centered">
        {{ html | safe }}
    </ol>
{%- endmacro %}

{% macro portraitbox(obj) -%}
    {% if obj.name -%}
        <figure class="portraitbox figure-stamp">
            <div class="portraitbox-heading">
                {{ obj.name }}
            </div>
            {{ obj.text | safe }}
        </figure>
    {%- endif %}
{%- endmacro %}

{% macro subpage_chapter(number, subtitle, class) -%}
    {% if subtitle -%}
        <div class="{{ class }}">
            <span>Kapitel {{ number }}</span>
            <span>&mdash; {{ subtitle }} &mdash;</span>
            <span></span>
        </div>
    {%- endif %}
{%- endmacro %}

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
        <div class="{{ class }}">
            <a name="kapitel{{ number }}"></a>
            {{ number }} &mdash; {{ subtitle }}
        </div>
    {% endif %}
{%- endmacro %}

{% macro intertitle(intertitle) -%}
    <h2 class="article__subheading is-constrained is-centered">
        {{ intertitle | striptags }}
    </h2>
{%- endmacro %}

{% macro raw(obj) -%}
    <div class="raw">{{ obj.xml | safe }}</div>
{%- endmacro %}

{% macro citation(obj) -%}
    <blockquote class="
        {% if obj.layout == 'wide' %}
            quote--wide
        {% else %}
            quote
        {% endif %}
    ">
        <span class="quote__text">{{ obj.text }}</span>
        {% if obj.attribution %}
            {% if obj.url %}
                <span class="quote__author">
                    <a href="{{ obj.url }}">
                        {{ obj.attribution }}
                    </a>
                </span>
            {% else %}
                <span class="quote__author">{{ obj.attribution }}</span>
            {% endif %}
        {% endif %}
    </blockquote>
{%- endmacro %}

{% macro advertising(ad) -%}
    {% if ad.type == 'rectangle' %}
        <div class="iqdplace" data-place="medrec_8"></div>
    {% endif %}
{%- endmacro %}

{% macro headerimagestandard(obj) -%}
    <div class="article__head__image">
        {% include "zeit.web.magazin:templates/inc/article/header-image.html" with context %}
    </div>
{%- endmacro %}

{% macro image(obj, loop) %}
    {# BBB Wrap the article image in a macro until we have block templates in ZMO #}
    {% include "zeit.web.magazin:templates/inc/asset/image_article.tpl" with context %}
{%- endmacro %}

{% macro headerimage(obj) -%}
    <div class="scaled-image is-pixelperfect article__head-image">
        {{ lama.insert_responsive_image(obj) }}
    </div>{{ obj.caption | safe }}{{ obj.copyright }}
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
                <span class="video__button">{{ lama.use_svg_icon('playbutton', 'video__play-icon', request) }}</span>
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

{% macro print_pagination( pagination ) -%}
    {% if pagination.total > 1 %}
    <nav class="article-pagination is-constrained is-centered" role="navigation" aria-labeledby="pagination-title">
        <div class="article-pagination__a11y-title" id="pagination-title">Seitennavigation</div>
        {% if pagination.next_page_title -%}
            <div class="article-pagination__nexttitle">
                <a href="{{ pagination.next_page_url }}">Auf Seite {{ pagination.current + 1 }} <span class="article-pagination__dash">—</span> {{ pagination.next_page_title }}</a>
            </div>
        {%- endif %}
        <ul class="article-pagination__pager">
            <li class="article-pagination__item">
                {%- if pagination.prev_page_url -%}
                    <a class="article-pagination__link" href="{{ pagination.prev_page_url }}">{{ lama.use_svg_icon('pagination-previous', 'article-pagination__icon article-pagination__icon--active', request) }}</a>
                {%- else -%}
                    {{ lama.use_svg_icon('pagination-previous', 'article-pagination__icon', request) }}
                {%- endif -%}
            </li>

            {% for url in pagination.pages_urls -%}
                {% set current_class = "article-pagination__link--current" if loop.index == pagination.current else "" %}
                <li class="article-pagination__item"><a class="article-pagination__link {{current_class}}" href="{{ url }}">{{ loop.index }}</a></li>
            {%- endfor %}

            <li class="article-pagination__item">
                {%- if pagination.next_page_url -%}
                    <a class="article-pagination__link" href="{{ pagination.next_page_url }}">{{ lama.use_svg_icon('pagination-next', 'article-pagination__icon article-pagination__icon--active', request) }}</a>
                {%- else -%}
                    {{ lama.use_svg_icon('pagination-next', 'article-pagination__icon article-pagination__icon--next', request) }}
                {%- endif -%}
            </li>
        </ul>
    </nav>
    {% endif %}
{%- endmacro %}

{% macro photocluster(obj) %}
<div class="photocluster__wrap">
    <div class="photocluster">
    {% if obj %}
        {% for entry in obj.itervalues() -%}
            <div class="photocluster__item">
                <div class="scaled-image">
                    {{ lama.insert_responsive_image(entry) }}
                </div>
            </div>
        {%- endfor %}
    {% endif %}
    </div>
    <div class="photocluster__caption is-constrained is-centered">
        <div class="photocluster__caption__text">
            {{ obj.galleryText | safe }}
        </div>
    </div>
</div>
{% endmacro %}

{% macro meta_author(authors, class="article__head__meta__author", titlecase=True) %}
    {%- if authors -%}
        {%- for author in authors -%}
            {%- if titlecase -%}
                {{ author.prefix | title }}
            {% else %}
                {{ author.prefix }}
            {% endif %}
            {%- if author.href -%}
                <a href="{{ author.href | create_url }}" class="{{ class }}" itemprop="url"><span itemprop="name">{{ author.name }}</span></a>{{ author.location }}
            {%- else -%}
                <span class="{{ class }}"><span itemprop="name">{{ author.name }}</span>{{ author.location }}</span>
            {%- endif -%}
            {{ author.suffix }}
        {%- endfor -%}
    {%- endif -%}
{% endmacro %}

{% macro inlinegallery(block) -%}
    {% include 'zeit.web.core:templates/inc/blocks/inlinegallery.html' %}
{%- endmacro %}

{% macro no_block(block) %}{% endmacro %}
