{% import 'templates/macros/layout_macro.tpl' as lama with context %}

{% macro place(item) -%}
    {{lama.adplace(item, view.banner_channel)}}
{%- endmacro %}

{% macro supertitle() -%}
  <h2 class="article__head__supertitle">{{ view.supertitle }}</h2>
{%- endmacro %}

{% macro title() -%}
  <h1 class="article__head__title">{{view.title}}</h1>
{%- endmacro %}

{% macro subtitle(include_meta=False, with_quotes=False) -%}
    <div class="article__head__subtitle">
        <p>
            {% if with_quotes %}
                »{{view.subtitle}}«
            {% else %}
                {{view.subtitle}}
            {% endif %}
            {% if include_meta and view.genre %}
                {{view.genre|title}}
            {% endif %}
            {% if include_meta and view.authors %}
                {{ meta_author(view.authors, titlecase=view.genre==None) }}
            {% endif %}
        </p>
    </div>
{%- endmacro %}

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
        <div class="article__subpage-index__title">&uuml;bersicht</div>
        {% for page in pages if page.teaser %}
            <div class="article__subpage-index__item">
                <span class="article__subpage-index__item__count">{{ page.number }} &mdash; </span>
                <span class="article__subpage-index__item__title-wrap">
                    {% if loop.index == number %}
                        <span class="article__subpage-index__item__title {{ active_class }}">{{ page.teaser }}</span>
                    {% else %}
                        <a href="#kapitel{{ loop.index }}" class="article__subpage-index__item__title js-scroll">{{  page.teaser  }}</a>
                    {% endif %}
                </span>
            </div>
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
        <span class="article__head__meta__source">{{ source }}</span>
    {% endif %}
    <span class="article__head__meta__date">{{ date }}</span>
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

{% macro headerimagestandard(obj) -%}
    <div class="article__head__image">
        {{ image(obj) }}
    </div>
{%- endmacro %}

{% macro image(obj) -%}
    <figure class="
        {% if obj.layout == 'large' or obj.layout == 'zmo-large-center' %}
            figure-full-width
        {% elif obj.layout == 'zmo-xl-header' %}
            figure-header
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
                {{ lama.insert_responsive_image(obj) }}
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
        {{ lama.insert_responsive_image(obj,'article__main-image--longform') }}
    </div>{{obj.caption}}{{obj.copyright}}
{%- endmacro %}

{% macro columnimage(obj) -%}
    <div class="article__column__headerimage">
        <div class="scaled-image">
            {{ lama.insert_responsive_image(obj) }}
        </div>
    </div>
{%- endmacro %}

{% macro meta_author(authors, class="article__head__meta__author", titlecase=True) %}
    {%- if authors -%}
        {%- for author in authors -%}
            {%- if titlecase -%}
                {{author.prefix|title}}
            {% else %}
                {{author.prefix}}
            {% endif %}
            {%- if author.href -%}
                <a href="{{author.href|translate_url}}" class="{{class}}">{{author.name}}</a>{{author.location}}
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
                <source src="http://live0.zeit.de/multimedia/videos/{{obj.id}}.webm" type="video/webm">
        </video>
        <img class="article__main-image--longform video--fallback" src="http://www.zeit.de/live0-backend/multimedia/videos/{{obj.id}}.jpg">
    </div>
{%- endmacro %}

{% macro comment(comment, featured) -%}
    <article class="comment{% if comment.indented and not featured %} is-indented{% endif %}"{% if not featured %} id="{{comment.cid}}"{% endif %}>
        <div class="comment__head">
            {% if comment.img_url -%}
            <img src="{{comment.img_url}}" class="comment__head__img" alt="" />
            {% endif -%}
            <div class="comment__head__meta">
                <strong class="comment__head__meta__name">{{comment.name|e}}</strong>
                <a href="#{{comment.cid}}" class="comment__head__meta__date{% if not featured %} js-scroll{% endif %}">{{comment.timestamp | format_date_ago()}}</a>
                {% if comment.role -%}
                <div class="comment__head__meta__label">{{comment.role}}</div>
                {% endif -%}
            </div>
        </div>
        <div class="comment__body">
            {{comment.text|safe}}
        </div>
        <aside class="comment__tools">
            {% if not comment.indented -%}
            <a class="comment__tools__icon icon-comment-reply js-reply-to-comment" data-cid="{{comment.cid|replace('cid-', '')}}" title="Auf Kommentar antworten">Auf Kommentar antworten</a>
            {% endif -%}
            <a class="comment__tools__icon icon-comment-report js-report-comment" data-cid="{{comment.cid|replace('cid-', '')}}" title="Kommentar melden">Kommentar melden</a>
        </aside>
    </article>
{%- endmacro %}

{% macro comments(obj, request) -%}
    {% if obj.comments is not none -%}
    <div class="article__socialbox tc" id="js-social-services">
        <div class="article__sharing">
            {% if obj.linkreach.total -%}
            <div class="article__sharing__item article__sharing__sum">
                <span class="article__sharing__total">{{ obj.linkreach.total[0] }}</span>
                <span class="article__sharing__unit">{{ obj.linkreach.total[1] }}</span>
            </div>
            {%- endif %}
            <div class="article__sharing__services">
                <a href="http://www.facebook.com/sharer/sharer.php?s=100&amp;p[url]={{request.url}}&amp;p[images][0]={{obj.sharing_img.video_still or obj.sharing_img|default_image_url}}&amp;p[title]={{obj.title}}&amp;p[summary]={{obj.subtitle}}"
                    target="_blank"
                    class="article__sharing__item js-has-popup"
                    data-width="600"
                    data-height="300">
                    <span class="article__sharing__services__icon icon-sharebox-facebook"></span>
                    <span class="article__sharing__services__text">{{ ' '.join(obj.linkreach.facebook) }}</span>
                </a>
                 <a href="http://twitter.com/home?status={{request.url}}"
                    target="_blank"
                    class="article__sharing__item js-has-popup"
                    data-width="600"
                    data-height="300">
                    <span class="article__sharing__services__icon icon-sharebox-twitter"></span>
                    <span class="article__sharing__services__text">{{ ' '.join(obj.linkreach.twitter) }}</span>
                </a>
                <a href="https://plus.google.com/share?url={{request.url}}"
                   target="_blank"
                   class="article__sharing__item js-has-popup"
                   data-width="480"
                   data-height="350">
                   <span class="article__sharing__services__icon icon-sharebox-google"></span>
                   <span class="article__sharing__services__text">{{ ' '.join(obj.linkreach.googleplus) }}</span>
               </a>
            </div>
            <div class="article__sharing__item">
                <a class="article__sharing__link js-toggle-sharing">
                    <span class="article__sharing__icon icon-sharebox-share"></span>
                    Teilen
                </a>
            </div>
        </div>

        <div class="article__comments-trigger">
            <a class="article__comments-trigger__link js-comments-trigger">
                <span class="article__comments-trigger__count icon-sharebox-close">{{comments['comment_count']}}</span>
                <span class="article__comments-trigger__text">{% if obj.comments.comment_count == 1 %}Kommentar{% else %}Kommentare{% endif %}</span>
            </a>
        </div>
    </div>
    <section class="comments" id="js-comments">
        <div class="comments__head" id="js-comments-head">
            {% if request.app_info.authenticated -%}
            <form action="{{comments['comment_post_url']}}" method="POST" class="comment__form" id="js-comments-form">
                <p>
                    <textarea name="comment" placeholder="Ihr Kommentar" class="js-required"></textarea>
                    <input type="hidden" name="nid" value="{{comments['nid']}}">
                    <input type="hidden" name="pid" value="">
                    <input type="hidden" name="uid" value="{{request.app_info.user.uid}}">
                </p>
                <div class="comment__form__note comment__form__note--casual">angemeldet als <a href="{{request.app_info.community_host}}user/{{request.app_info.user.uid}}">{{request.app_info.user.name|e}}</a></div>
                <div class="comment__form__actions">
                    <input type="submit" class="button" value="Kommentieren" disabled />
                </div>
            </form>
            {% else -%}
            <form class="comment__form comment__form--login" id="js-comments-form">
                <div class="comment__form__wrap">
                    <div class="comment__form__note">Bitte melden Sie sich an, um zu kommentieren.</div>
                </div>
                <a href="{{request.app_info.community_host}}{{request.app_info.community_paths.login}}?destination={{request.url|e}}" class="button">Anmelden</a>
                <a href="{{request.app_info.community_host}}{{request.app_info.community_paths.register}}?destination={{request.url|e}}" class="button">Registrieren</a>
            </form>
            {% endif -%}
        </div>
        <div class="tabs has-2">
            <div class="tabs__head" id="js-comments-tabs-head">
                <a href="#tab1" class="tabs__head__tab is-active">Alle</a>
                <a href="#tab2" class="tabs__head__tab">Ausgewählte</a>
            </div>
            <div class="comments__body" id="js-comments-body">
                <div class="tabs__content is-active">
                    <div class="comments__list" id="tab1">
                        {% for commentdict in comments['comments'] %}
                            {{ comment(commentdict, false) }}
                        {% endfor %}
                    </div>
                </div>
                <div class="tabs__content">
                    <div class="comments__list" id="tab2">
                        {% for commentdict in comments['comments'] %}
                            {% if commentdict['recommended'] -%}
                                {{ comment(commentdict, true) }}
                            {%- endif %}
                        {% endfor %}
                    </div>
                </div>
                <div class="comments__button__newer" id="js-comments-button-up">
                    <div class="button icon-comments-newer js-scroll-comments" data-direction="up">Neuere</div>
                </div>
            </div>
        </div>
        <div class="comments__button__older" id="js-comments-button-down">
            <div class="button icon-comments-older js-scroll-comments" data-direction="down">Ältere</div>
        </div>
        <script type="text/template" id="js-report-success-template">
            <div class="comment__form__success">
                <span class="comment__icon--40 icon-check-kommentar-gesendet"></span>
                <div class="comment__form__success__text">Danke! Ihre Meldung wird an die Redaktion weitergeleitet.</div>
            </div>
        </script>
        <script type="text/template" id="js-report-comment-template">
            {% if request.app_info.authenticated -%}
            <form action="{{obj.comments.comment_report_url}}" method="POST" class="comment__form" style="display: none">
                <p><textarea name="note" placeholder="Warum halten Sie diesen Kommentar für bedenklich?" class="js-required"></textarea></p>
                <p class="comment__form__text">
                    Nutzen Sie dieses Fenster, um Verstöße gegen die <a target="_blank" href="http://www.zeit.de/administratives/2010-03/netiquette">Netiquette</a> zu melden.
                    Wenn Sie einem Kommentar inhaltlich widersprechen möchten, <a href="#js-comments-form" class="js-scroll">nutzen Sie das Kommentarformular</a> und beteiligen Sie sich an der Diskussion.
                </p>
                <p class="comment__form__actions">
                    <input type="hidden" name="uid" value="{{request.app_info.user.uid}}">
                    <input type="hidden" name="content_id" value="<%- commentId %>">
                    <a href="#" class="js-cancel-report">Abbrechen</a><button disabled="disabled" class="button js-submit-report" type="button">Abschicken</button>
                </p>
            </form>
            {% else -%}
            <form class="comment__form comment__form--login" style="display: none">
                <div class="comment__form__wrap">
                    <div class="comment__form__note">Bitte melden Sie sich an, um diesen Kommentar zu melden.</div>
                </div>
                <a href="{{request.app_info.community_host}}{{request.app_info.community_paths.login}}?destination={{request.url|e}}" class="button">Anmelden</a>
                <a href="{{request.app_info.community_host}}{{request.app_info.community_paths.register}}?destination={{request.url|e}}" class="button">Registrieren</a>
            </form>
            {% endif -%}
        </script>
    </section>
    {%- endif %}
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
            var el = document.getElementsByClassName('article__head__meta__date');
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
