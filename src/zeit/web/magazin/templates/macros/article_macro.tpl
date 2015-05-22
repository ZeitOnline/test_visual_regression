{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama_core with context%}
{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}
{% extends 'zeit.web.core:templates/macros/article_macro.tpl' %}

{% macro place(item) -%}
    {{ lama_core.adplace(item, view) }}
    {{ lama_core.adplace_middle_mobile(item) }}
{%- endmacro %}

{% macro contentadblock(item) -%}
    {{ lama_core.content_ad_article(view) }}
{%- endmacro %}

{% macro supertitle() -%}
  {#
    view = {'supertitle': u'Streik der Lokführer'}
  #}
  <div class="article__head__supertitle">{{ view.supertitle | hide_none }}</div>
{%- endmacro %}

{% macro title() -%}
  {#
    view = {'title': u'Japan und China kommen sich näher'}
  #}
  <div class="article__head__title">{{ view.title | hide_none }}</div>
{%- endmacro %}

{% macro subtitle(include_meta=False, with_quotes=False) -%}
  {#
    include_meta = True
    with_quotes = True
    view = {'subtitle': u'Historischer Händedruck: Chinas Präsident Xi und '
                        u'Japans Premier Abe haben sich in Peking getroffen. '
                        u'Beide Staaten wollen ihre Beziehungen neu beleben.',
            'genre': 'Politik',
            'authors': ['Ursula Finkel', 'Marcel Fassbinder']
            }
  #}
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

{% macro liveblog(obj) -%}
    {% if obj.blog_id -%}
        <div class="is-constrained is-centered">
            {# TODO: We should mock the liveblog backend for local testing. #}
            <esi:include src="http://www.zeit.de/liveblog-backend/{{ obj.blog_id }}.html" onerror="continue" />
        </div>
    {%- endif %}
{%- endmacro %}

{% macro paragraph(html, class) -%}
  {#
    html = (u'Sieben Begriffe für ein und denselben <i>Gegenstand</i> – das ist '
            u'deutsches Kulturgut. <b>Dialekte</b> gehören schon immer zu diesem '
            u'viel durchwanderten und umkämpften Land. Auch die deutsche '
            u'Teilung hat zur <a href="#">sprachlichen Vielfalt</a> beigetragen.')
  #}
    <p class="is-constrained is-centered">
        {{ html | safe}}
    </p>
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

{% macro subpage_chapter(number, subtitle, class) -%}
  {#
    number = 4
    subtitle = (u'Am Potsdamer Platz steigen Ballons der symbolischen '
                u'Lichtgrenze gen Himmel.')
  #}
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
        {{ intertitle|striptags }}
    </h2>
{%- endmacro %}

{% macro raw(obj) -%}
    <div class="raw">{{ obj.xml|safe }}</div>
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

{% macro image(obj, loop) -%}
    {% if obj | default_image_url -%}
        <figure class="
            {%- if obj.layout == 'large' or obj.layout == 'zmo-large-center' -%}
                figure-full-width
            {%- elif obj.layout == 'zmo-xl-header' -%}
                figure-header
            {%- elif obj.layout == 'zmo-medium-left' -%}
                figure-horizontal
            {%- elif obj.layout == 'zmo-medium-right' -%}
                figure-horizontal--right
            {%- elif obj.layout == 'zmo-medium-center' -%}
                figure is-constrained is-centered
            {%- elif obj.layout == 'zmo-small-left' -%}
                figure-stamp
            {%- elif obj.layout == 'zmo-small-right' -%}
                figure-stamp--right
            {%- else -%}
                figure-stamp
            {%- endif -%}
            ">
            <div class="scaled-image">
                {{ lama.insert_responsive_image(obj, None, 'article') }}
            </div>
            <figcaption class="figure__caption">
                {% if loop -%}
                <span class="figure__index">{{ loop.index }}/{{ loop.length }}</span>
                {% endif -%}
                <span class="figure__text">{{ obj.caption | hide_none | safe }}</span>
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

{% macro headerimage(obj) -%}
    <div class="scaled-image is-pixelperfect article__head-image">
        {{ lama.insert_responsive_image(obj) }}
    </div>{{ obj.caption | hide_none | safe }}{{ obj.copyright }}
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
        {% endif %}" data-video="{{ obj.id }}">
            <div class="video__still">
                <img class="figure__media" src="{{ obj.video_still| default('http://placehold.it/160x90', true) }}" alt="Video: {{ obj.title }}" title="Video: {{ obj.title }}">
                <span class="video__button"></span>
            </div>
            <figcaption class="figure__caption">
                    {{ obj.description }}
            </figcaption>
        </figure>
    {%- endif %}
{%- endmacro %}

{% macro headervideo(obj, wrap_class='article__main-video--longform', img_class='') -%}

    {% if obj.id is not defined and obj.uniqueId -%}
        {% set id = obj.uniqueId|substring_from('/') %}
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

{% macro comment(comment) -%}
    <article class="comment{% if comment.is_reply and not comment.is_promoted %} is-indented{% endif %}"{% if not comment.is_promoted %} id="cid-{{ comment.cid }}"{% endif %}>
        <div class="comment__head">
            {% if comment.img_url -%}
            <span class="comment__head__avatar" style="background-image: url('{{ comment.img_url }}')"></span>
            {% endif -%}
            <div class="comment__head__meta">
                <a class="comment__head__meta__name" href="{{ comment.userprofile_url }}">{{ comment.name|e }}</a>
                <a href="#cid-{{ comment.cid }}" class="comment__head__meta__date{% if not comment.is_promoted %} js-scroll{% endif %}">{{ comment.created | format_comment_date }}</a>
                {% if comment.role -%}
                <div class="comment__head__meta__label">{{ comment.role }}</div>
                {% endif -%}
            </div>
        </div>
        <div class="comment__body">
            {{ comment.text|safe }}
        </div>
        <aside class="comment__tools">
            {% if not comment.is_reply -%}
            <a class="comment__tools__icon icon-comment-reply js-reply-to-comment" data-cid="{{ comment.cid }}" title="Auf Kommentar antworten">Auf Kommentar antworten</a>
            {% endif -%}
            <a class="comment__tools__icon icon-comment-report js-report-comment" data-cid="{{ comment.cid }}" title="Kommentar melden">Kommentar melden</a>
        </aside>
    </article>
{%- endmacro %}

{% macro comments(obj, request) -%}
    {% if obj.comments is not none -%}
    <div class="article__socialbox tc" id="js-social-services">
        <div class="article__sharing">
            {% if obj.linkreach.total -%}
            <div class="article__sharing__item article__sharing__sum js-toggle-sharing">
                <span class="article__sharing__total">{{ obj.linkreach.total[0] }}</span>
                <span class="article__sharing__unit">{{ obj.linkreach.total[1] }}</span>
            </div>
            {%- endif %}
            <div class="article__sharing__services blind">
                <a href="http://www.facebook.com/sharer/sharer.php?u={{ view.content_url + '?wt_zmc=sm.int.zonaudev.facebook.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=facebook_zonaudev_int&utm_campaign=facebook_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" class="article__sharing__item">
                    <span class="article__sharing__services__icon icon-sharebox-facebook"></span>
                    <span class="article__sharing__services__text">{{ ' '.join(obj.linkreach.facebook) }}</span>
                </a>
                <a href="http://twitter.com/intent/tweet?text={{ view.title | urlencode }}&via=zeitonline&url={{ view.content_url + '?wt_zmc=sm.int.zonaudev.twitter.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=twitter_zonaudev_int&utm_campaign=twitter_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" class="article__sharing__item">
                    <span class="article__sharing__services__icon icon-sharebox-twitter"></span>
                    <span class="article__sharing__services__text">{{ ' '.join(obj.linkreach.twitter) }}</span>
                </a>
                <a href="https://plus.google.com/share?url={{ view.content_url + '?wt_zmc=sm.int.zonaudev.gplus.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=gplus_zonaudev_int&utm_campaign=gplus_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" class="article__sharing__item">
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
                <span class="article__comments-trigger__count icon-sharebox-close">{{ obj.comments.comment_count }}</span>
                <span class="article__comments-trigger__text">{% if obj.comments.comment_count == 1 %}Kommentar{% else %}Kommentare{% endif %}</span>
            </a>
        </div>
    </div>
    <section class="comments" id="js-comments">
        <div class="comments__head" id="js-comments-head">
            {% if request.authenticated_userid -%}
            <form action="{{ obj.comments.comment_post_url }}" method="POST" class="comment__form" id="js-comments-form">
                <p>
                    <textarea name="comment" placeholder="Ihr Kommentar" class="js-required"></textarea>
                    <input type="hidden" name="nid" value="{{ obj.comments.nid }}">
                    <input type="hidden" name="pid" value="">
                    <input type="hidden" name="uid" value="{{ request.session.user.uid }}">
                </p>
                <div class="comment__form__note comment__form__note--casual">angemeldet als <a href="{{ request.registry.settings.community_host }}/user/{{ request.session.user.uid }}">{{ request.session.user.name|e }}</a></div>
                <div class="comment__form__actions">
                    <input type="submit" class="button" value="Kommentieren" disabled />
                </div>
            </form>
            {% else -%}
            <form class="comment__form comment__form--login" id="js-comments-form">
                <div class="comment__form__wrap">
                    <div class="comment__form__note">Bitte melden Sie sich an, um zu kommentieren.</div>
                </div>
                <a href="{{ request.registry.settings.community_host }}/user/login?destination={{ request.url|e }}" class="button">Anmelden</a>
                <a href="{{ request.registry.settings.community_host }}/user/register?destination={{ request.url|e }}" class="button">Registrieren</a>
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
                        {% for commentdict in obj.comments.comments %}
                            {{ comment(commentdict) }}
                        {% endfor %}
                    </div>
                </div>
                <div class="tabs__content">
                    <div class="comments__list" id="tab2">
                        {% for commentdict in obj.comments.comments %}
                            {% if commentdict.is_promoted -%}
                                {{ comment(commentdict) }}
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
            {% if request.authenticated_userid -%}
            <form action="{{ obj.comments.comment_report_url }}" method="POST" class="comment__form" style="display: none">
                <p><textarea name="note" placeholder="Warum halten Sie diesen Kommentar für bedenklich?" class="js-required"></textarea></p>
                <p class="comment__form__text">
                    Nutzen Sie dieses Fenster, um Verstöße gegen die <a target="_blank" href="http://{{ request.host }}/administratives/2010-03/netiquette">Netiquette</a> zu melden.
                    Wenn Sie einem Kommentar inhaltlich widersprechen möchten, <a href="#js-comments-form" class="js-scroll">nutzen Sie das Kommentarformular</a> und beteiligen Sie sich an der Diskussion.
                </p>
                <p class="comment__form__actions">
                    <input type="hidden" name="uid" value="{{ request.session.user.uid }}">
                    <input type="hidden" name="content_id" value="<% commentId %>">
                    <a href="#" class="js-cancel-report">Abbrechen</a><button disabled="disabled" class="button js-submit-report" type="button">Abschicken</button>
                </p>
            </form>
            {% else -%}
            <form class="comment__form comment__form--login" style="display: none">
                <div class="comment__form__wrap">
                    <div class="comment__form__note">Bitte melden Sie sich an, um diesen Kommentar zu melden.</div>
                </div>
                <a href="{{ request.registry.settings.community_host }}/user/login?destination={{ request.url|e }}" class="button">Anmelden</a>
                <a href="{{ request.registry.settings.community_host }}/user/register?destination={{ request.url|e }}" class="button">Registrieren</a>
            </form>
            {% endif -%}
        </script>
    </section>
    {%- endif %}
{%- endmacro %}

{% macro add_publish_date( lm_date, publish_date, format) -%}
    {% if lm_date %}
        <!--[if gt IE 8]><!-->
        <script type="text/javascript">
        //due to seo reasons, original publish date is added later
            var el = document.getElementsByClassName('article__head__meta__date');
            var content = el[0].textContent != undefined ? el[0].textContent : el[0].innerText;
            if( content != undefined ){
                if( '{{ format }}' === 'long' ){
                    el[0].innerHTML = '{{ publish_date }} —<br><span>zuletzt aktualisiert am ' + content + '</span>';
                }else{
                    el[0].innerHTML = '{{ publish_date }} —<br><span>editiert: ' + content + '</span>';
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
                <a href="{{ pagination.next_page_url }}">Auf Seite {{ pagination.current + 1 }} <span class="article__pagination__dash">—</span> {{ pagination.next_page_title }}</a>
            </div>
        {%- endif %}
        <ul class="article__pager">
            {% if pagination.prev_page_url %}
                <li class="article__pager__prev"><a class="icon-pagination-previous" href="{{ pagination.prev_page_url }}">Zurück</a></li>
            {% else %}
                <li class="article__pager__prev is-inactive"><span class="icon-pagination-previous">Zurück</span></li>
            {% endif %}

            {% for url in pagination.pages_urls -%}
                {% set current_class = "is-current" if loop.index == pagination.current else "" %}
                <li class="article__pager__number {{ current_class }}"><a href="{{ url }}">{{ loop.index }}</a></li>
            {%- endfor %}


            {% if pagination.next_page_url %}
                <li class="article__pager__next"><a class="icon-pagination-next" href="{{ pagination.next_page_url }}">Vor</a></li>
            {% else %}
                <li class="article__pager__next is-inactive"><span class="icon-pagination-next">Vor</span></li>
            {% endif %}
        </ul>
    </div>
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
