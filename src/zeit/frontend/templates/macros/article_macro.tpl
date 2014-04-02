
{% macro paragraph(html, class) -%}
    <p class="is-constrained is-centered">
        {{ html | safe}}
    </p>
{%- endmacro %}

{% macro subpage_chapter(number, subtitle, class) -%}
    {% if subtitle %}
        <div class="{{ class }}">
            <span>Kapitel {{ number }}</span>
            <span>&mdash; {{ subtitle }} &mdash;</span>
            <span></span>
        </div>
    {% endif %}
{%- endmacro %}

{% macro subpage_index(pages, subtitle, number, index_class, active_class) -%}
    {% if subtitle %}
        <div class="{{ index_class }}">
        {% for page in pages if page.teaser %}
            {% if loop.index == number %}
                <span class="{{ active_class }}">{{ page.number }} — {{ page.teaser }}</span>
            {% else %}
                <span><a href="#kapitel{{ loop.index }}">{{ page.number }} — {{  page.teaser  }}</a></span>
            {% endif %}
        {% endfor %}
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

{% macro source_date(date, source) -%}
    {% if source %}
        <span class="article__meta__second__source">{{ source }}</span>
    {% endif %}
    <span class="article__meta__second__date">{{ date }}</span>
{%- endmacro %}

{% macro intertitle(intertitle) -%}
    <h3 class="article__subheading is-constrained is-centered">
        {{ intertitle|striptags }}
    </h3>
{%- endmacro %}

{% macro raw(obj) -%}
    <div class="raw">{{obj.xml|safe}}</div>
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

{% macro image(obj) -%}
    <figure class="
        {% if obj.layout == 'large' or obj.layout == 'zmo-large-center' %}
            figure-full-width
        {% elif obj.layout == 'zmo-xl' %}
            article__main-image figure-full-width
        {% elif obj.layout == 'zmo-medium-left' %}
            figure-horizontal
        {% elif obj.layout == 'zmo-medium-right' %}
            figure-horizontal--right
        {% elif obj.layout == 'zmo-medium-center' %}
            figure is-constrained is-centered
        {% elif obj.layout == 'zmo-small-left' %}
            figure-stamp
        {% elif obj.layout == 'zmo-small-right' %}
            figure-stamp--right
        {% else %}
            figure-stamp
        {% endif %}
        ">
            <div class="scaled-image">
                <!--[if gte IE 9]> -->
                <noscript data-ratio="{{obj.ratio}}">
                <!-- <![endif]-->
                        <img alt="{{obj.attr_alt}}" title="{{obj.attr_title}}" class="figure__media" src="{{obj | default_image_url | default('http://placehold.it/160x90', true)}}" data-ratio="{{obj.ratio}}">
                <!--[if gte IE 9]> -->
                </noscript>
                <!-- <![endif]-->
            </div>
            <figcaption class="figure__caption">
                {{obj.caption}}
                {% if obj.copyright != '©' %}
                <span class="figure__copyright">{{obj.copyright}}</span>
                {% endif %}
            </figcaption>
    </figure>
{%- endmacro %}

{% macro inlinegalleryimage(obj) -%}
    {{ image(obj) }}
{%- endmacro %}

{% macro headerimage(obj) -%}
    <div class="scaled-image is-pixelperfect">
        <!--[if gte IE 9]> -->
        <noscript>
        <!-- <![endif]-->
            <img class="article__main-image--longform" src="{{obj | default_image_url | default('http://placehold.it/160x90', true)}}">
        <!--[if gte IE 9]> -->
        </noscript>
        <!-- <![endif]-->
    </div>{{obj.caption}}{{obj.copyright}}
{%- endmacro %}

{% macro meta_author(authors, class="article__meta__author") %}
    {%- if authors -%}
        {%- for author in authors -%}
            {{author.prefix}}
            {%- if author.href -%}
                <a href="{{author.href|translate_url}}" class="{{class}} meta-link">{{author.name}}</a>{{author.location}}
            {%- else -%}
                <span class="{{class}}">{{author.name}}{{author.location}}</span>
            {%- endif -%}
            {{author.suffix}}
        {%- endfor -%}
    {%- endif -%}
{% endmacro %}

{% macro focussed_nextread( nextread ) -%}
    {%-if nextread -%}
      {% set layout = nextread['layout'] %}
      {% set image = nextread['image'] %}
      {% set article = nextread['article'] %}
        <aside class="article__nextread nextread-{{layout}} is-centered">
            <div class="article__nextread__lead">Lesen Sie jetzt:</div>
            <a title="{{ article.supertitle }}: {{ article.title }}" href="{{ article.uniqueId|translate_url }}">
                {% if layout == "maximal"%}
                <div class="article__nextread__body is-centered" style="background-image:url({{ image['uniqueId'] }});">
                {% else %}
                <div class="article__nextread__body is-centered">
                {% endif %}
                    {% if layout == "base" and image %}
                        <img title="{{ image['caption'] }}" alt="{{ image['caption'] }}" src="{{ image['uniqueId']|translate_url }}">
                    {% endif %}
                    <div class="article__nextread__article">
                        <span class="article__nextread__supertitle">{{ article.supertitle }}</span>
                        <span class="article__nextread__title">{{ article.title }}</span>
                    </div>
                </div>
            </a>
        </aside>
    {%- endif -%}
{%- endmacro %}

{% macro video(obj) -%}
    {% if obj.id and obj.format != 'zmo-xl-header' -%}
        <figure class="
        {% if obj.format == 'zmo-small-left' or obj.format == 'small' %}
            figure-stamp
        {% elif obj.format == 'large' or obj.format == 'zmo-large-left' or obj.format == 'zmo-large-center' or obj.format == 'zmo-large-right' %}
            figure-full-width
        {% elif obj.format == 'zmo-small-right' %}
             figure-stamp--right
        {% else %}
             figure is-constrained is-centered
        {% endif %}" data-video="{{obj.id}}">
            <div class="video__still">
                <img class="figure__media" src="{{obj.video_still| default('http://placehold.it/160x90', true)}}">
                <span class="video__button"></span>
            </div>
            <figcaption class="figure__caption">
                    {{obj.description}}
            </figcaption>
        </figure>
    {%- endif %}
{%- endmacro %}

{% macro headervideo(obj) -%}
    <div data-backgroundvideo="{{obj.id}}" class="article__main-video--longform">
        <video preload="auto" autoplay="true" loop="loop" muted="muted" volume="0" poster="{{obj.video_still}}">
                <source src="{{obj.source}}" type="video/mp4">
                <source src="http://opendata.zeit.de/zmo-videos/{{obj.id}}.webm" type="video/webm">
        </video>
        <img class="article__main-image--longform video--fallback" src="{{obj.video_still}}">
    </div>
{%- endmacro %}

{% macro comment(indented, img_url, name, timestamp, role, text) -%}
    <article class="comment {% if indented -%}is-indented{%- endif %}">
        <div class="comment__head">
            {% if img_url -%}
                <img src="{{img_url}}" class="comment__head__img" />
            {%- endif %}
            <div class="comment__head__meta">
                <strong class="comment__head__meta__name">{{name}}</strong>
                <a href="#" class="comment__head__meta__date">{{timestamp}}</a>
            </div>
        </div>
        <div class="comment__body">
            <p>{{text|safe}}</p>
        </div>
        <aside class="comment__tools">
            <a class="comment__tools__flag icon-flag">Kommentar melden</a>
            {% if not indented -%}<a href="#js-comments-head-form" class="comment__tools__reply icon-reply">Auf Kommentar antworten</a>{%- endif %}
        </aside>
    </article>
{%- endmacro %}

{% macro comments(comments) -%}
    {% if comments is not none -%}
    <div class="tc">
        <div class="article__comments-trigger" id="js-comments-trigger">
            <div class="article__comments-trigger__wrap">
                <span class="article__comments-trigger__count icon-close-comments">{{comments['comment_count']}}</span>
                Kommentare
            </div>
        </div>
    </div>
    <section class="comments" id="js-comments">
        <div class="comments__head" id="js-comments-head">
            <form action="{{request.registry.settings.agatho_url[:-1]+request.path}}?destination={{request.url}}" method="POST" class="comments__head__form" id="js-comments-head-form">
                <textarea id="comment_msg" name="comment" placeholder="Ich denke …"></textarea>
                <input type="submit" class="button" value="Kommentieren" />
                <input id="subject msg" type="hidden" value="default subject zmo to be replaced by js" name="subject">
                <input id="node_id" type="hidden" value="{{comments['nid']}}" name="nid">
                <input id="parent_id" type="hidden" value="" name="pid">
                <input id="user_id" type="hidden" value="{{comments['my_uid']}}" name="uid">
            </form>
        </div>
        <div class="tabs has-2">
            <div class="tabs__head" id="js-comments-tabs-head">
                <a href="#tab1" class="tabs__head__tab is-active">Alle</a>
                <a href="#tab2" class="tabs__head__tab">Ausgewählte</a>
            </div>
            <div class="comments__body" id="js-comments-body">
                <div class="tabs__content is-active">
                    <a name="tab1"></a>
                    <div class="comments__list">
                        {% for commentdict in comments['comments'] %}
                            {{ comment(**commentdict) }}
                        {% endfor %}
                    </div>
                </div>
                <div class="tabs__content">
                    <a name="tab2"></a>
                    <div class="comments__list">
                    </div>
                </div>
                <div class="comments__body__newer">
                    <div class="button icon-comments-newer-inactive" id="js-comments-body-newer">Neuere</div>
                </div>
                <div class="comments__body__older">
                    <div class="button icon-comments-older-inactive" id="js-comments-body-older">Ältere</div>
                </div>
            </div>
        </div>
    </section>
    {%- endif %}

    <div class="tc">
        <div class="article__comments-trigger">
            <div class="article__comments-trigger__wrap">
                Kommentar hinzufügen
            </div>
        </div>
    </div>


{%- endmacro %}

{% macro inlinegallery(obj) -%}
    <div class="figure figure-full-width">
        <div class="inline-gallery">
            {% for item in obj.items() %}
                <!-- Gallery-Items as block.image(obj) -->
               {{ inlinegalleryimage(item) }}
            {% endfor %}
        </div>
    </div>
{%- endmacro %}

{% macro add_publish_date( lm_date, publish_date, format) -%}
    {% if lm_date %}
        <!--[if gt IE 8]><!-->
        <script type="text/javascript">
        //due to seo reasons, original publish date is added later
            var el = document.getElementsByClassName('article__meta__second__date');
            var content = el[0].innerText;
            if( content != undefined ){
                if( '{{format}}' === 'long' ){
                    el[0].innerHTML = '{{publish_date}}<span>zuletzt aktualisiert am ' + content + '</span>';
                }else{
                    el[0].innerHTML = '{{publish_date}}<span>editiert: ' + content + '</span>';
                }
            }
        </script>
        <!--<![endif]-->
    {% endif %}
{%- endmacro %}

{% macro print_pagination( pagination ) -%}
    {% if pagination.total > 1 %}
    <div class="article__pagination is-constrained is-centered" role="navigation" aria-labeledby="pagination-title">
        <div class="paginator__a11y__title is-audible" id="pagination-title" style="display:none">Seitennavigation</div> <!-- nach unsichtbar verschieben -->
        {% if pagination.next_page_title -%}
            <div class="article__pagination__nexttitle">
                <a href="{{pagination.next_page_url}}">Auf Seite {{pagination.current + 1}} <span class="paginator__dash">—</span> {{pagination.next_page_title}}</a>
            </div>
        {%- endif %}
        <ul class="article__pager">
            {% if pagination.prev_page_url %}
                <li class="article__pager__prev">
                    <a class="icon-paginierungs-pfeil-links" href="{{pagination.prev_page_url}}">Zurück</a>
                </li>
            {% else %}
                <li class="article__pager__prev is-inactive"><span class="icon-paginierungs-pfeil-links-inaktiv">Zurück</span></li>
            {% endif %}

            {% for url in pagination.pages_urls -%}
                {% set current_class = "is-current" if loop.index == pagination.current else "" %}
                <li class="article__pager__number {{current_class}}"><a href="{{url}}">{{loop.index}}</a></li>
            {%- endfor %}

            
            {% if pagination.next_page_url %}
                <li class="article__pager__next"><a class="icon-paginierungs-pfeil-rechts" href="{{pagination.next_page_url}}">Vor</a></li>
            {% else %}
                <li class="article__pager__next is-inactive"><span class="icon-paginierungs-pfeil-rechts-inaktiv">Vor</span></li>
            {% endif %}
        </ul>
    </div>
    {% endif %}
{%- endmacro %}
       
<!-- We use this, if for some reason or block is None -->
{% macro no_block(obj) %}
{% endmacro %}


