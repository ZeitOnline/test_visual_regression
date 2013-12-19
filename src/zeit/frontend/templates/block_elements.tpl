{% macro main_nav(breadcrumb, is_full_width) -%}
    <nav class="main-nav has-hover {% if is_full_width %}is-full-width{% endif %}" id="js-main-nav" itemscope itemtype="http://schema.org/SiteNavigationElement">
        <div class="main-nav__wrap">
            <a href="http://zeit.de/magazin" class="main-nav__logo" itemscope itemtype="http://schema.org/Organization">
                <meta itemprop="name" content="Zeit Online">
                <div class="main-nav__logo__wrap">
                    <img src="/img/zeit-logo--magazin.png" class="main-nav__logo__img" itemprop="logo" title="Nachrichten auf ZEIT ONLINE" alt="Nachrichten auf ZEIT ONLINE" />
                </div>
            </a>
            <div class="main-nav__menu">
                <header class="main-nav__menu__head" id="js-main-nav-trigger">
                    <div class="main-nav__menu__head__headline">ZEIT Magazin</div>
                    <div class="main-nav__menu__head__hamburger">Menu Öffnen</div>
                </header>
                <div class="main-nav__menu__content" id="js-main-nav-content">
                    <div class="main-nav__section main-nav__ressorts">
                        <div class="main-nav__section__content is-always-open" id="js-main-nav-ressorts-slider-container">
                            <div class="main-nav__ressorts__slider-arrow--left icon-arrow-left is-inactive"></div>
                            <div class="main-nav__ressorts__slider-arrow--right icon-arrow-right"></div>
                            <div class="main-nav__section__content__wrap" id="js-main-nav-ressorts-slider-strip">
                                <a href="#">Mode</a>
                                <a href="#">Essen & Trinken</a>
                                <a href="#">Veganes Leben</a>
                                <a href="#">Wochenmarkt</a>
                                <a href="#">Design</a>
                                <a href="#">Gesellschaft</a>
                                <a href="#">Bartpflege</a>
                            </div>
                        </div>
                    </div>
                    <a href="http://zeit.de" class="main-nav__menu__content__current-ressort" id="js-main-nav-current-ressort">Startseite ZEIT Online</a>
                    <div class="main-nav__section main-nav__all-ressorts">
                        <span class="main-nav__section__trigger icon-arrow-down">
                            Alle Ressorts
                        </span>
                        <div class="main-nav__section__content" id="js-main-nav-all-ressorts-content">
                            <div class="main-nav__section__content__wrap">
                                <a href="#">Politik</a>
                                <a href="#">Wirtschaft</a>
                                <a href="#">Gesellschaft</a>
                                <a href="#">Kultur</a>
                                <a href="#">Wissen</a>
                                <a href="#">Digital</a>
                                <a href="#">Studium</a>
                                <a href="#">Karriere</a>
                                <a href="#" class="is-active">Magazin</a>
                                <a href="#">Reisen</a>
                                <a href="#">Mobilität</a>
                                <a href="#">Sport</a>
                            </div>
                        </div>
                    </div>
                    <div class="main-nav__section main-nav__service-primary">
                        <div class="main-nav__section__content is-always-open">
                            <a href="#">Abo</a>
                            <a href="#">Shop</a>
                            <a href="#">ePaper</a>
                        </div>
                    </div>
                    <div class="main-nav__section main-nav__service">
                        <span class="main-nav__section__trigger icon-arrow-down">Service</span>
                        <div class="main-nav__section__content">
                            <div class="main-nav__section__content__wrap">
                                <a href="#">ZEITCampus</a>
                                <a href="#">ZEITGeschichte</a>
                                <a href="#">ZEITWissen</a>
                                <a href="#">Partnersuche</a>
                                <a href="#">Immobilien</a>
                                <a href="#">Automarkt</a>
                                <a href="#">Jobs</a>
                                <a href="#">Reiseangebote</a>
                                <a href="#">Apps</a>
                                <a href="#">Audio</a>
                                <a href="#">Archiv</a>
                                <a href="#">Spiele</a>
                            </div>
                        </div>
                    </div>
                    <div class="main-nav__section main-nav__search">
                        <span class="main-nav__section__trigger icon-search">Suche</span>
                        <div class="main-nav__section__content">
                            <div class="main-nav__search__form">
                                <input class="main-nav__search__input" type="text" size="20" placeholder="Suchbegriff …">
                                <input class="main-nav__search__submit" type="submit" value="Suchen">
                            </div>
                        </div>
                    </div>
                    <div class="main-nav__section main-nav__community">
                        <span class="main-nav__section__trigger">
                            <img src="/img/exner.jpg" class="main-nav__community__avatar">
                            Community
                        </span>
                        <div class="main-nav__section__content">
                            <a href="#">Account</a>
                            <a href="#">Logout</a>
                        </div>
                    </div>
                    <div class="main-nav__section main-nav__breadcrumbs">
                        <div class="main-nav__section__content is-always-open">
                            {{ breadcrumbs(breadcrumb, is_full_width) }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>
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

{% macro breadcrumbs(crumbs, is_full_width) -%}
    <div class="breadcrumbs-wrap {% if is_full_width %}is-full-width{% endif %}">
        <div class="breadcrumbs" id="js-breadcrumbs">
            <div class="breadcrumbs__trigger" id="js-breadcrumbs__trigger" data-alternate="Schlie&szlig;en">Wo bin ich?</div>
            <div class="breadcrumbs__list">
                <div class="breadcrumbs__list__item" itemprop="breadcrumb">
                    {% for crumb in crumbs %}
                        <a href="{{crumb[1]}}">{{crumb[0]}}</a>
                        {% if not loop.last %}
                          &rsaquo;
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
{%- endmacro %}

{% macro subpage_index(pages, subtitle, number, index_class, active_class) -%}
    {% if subtitle %}
        <div class="{{ index_class }}">
        {% for page in pages if page.teaser %}
            {% if loop.index == number %}
                <span class="{{ active_class }}">{{ page.number }} -- {{ page.teaser }}</span>
            {% else %}
                <span><a href="#kapitel{{ loop.index }}">{{ page.number }} -- {{  page.teaser  }}</a></span>
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

{% macro author_date(date, source) -%}
    <span class="article__meta__source">Aus {{ source }}</span><span class="article__meta__date">{{ date }}</span>
{%- endmacro %}

{% macro intertitle(intertitle) -%}
    <h3 class="article__subheading is-constrained is-centered">
        {{ intertitle }}
    </h3>
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
        {% if obj.layout == 'large' %}
            figure-full-width
        {% elif obj.layout == 'zmo-xl' %}
            article__main-image figure-full-width
        {% elif obj.layout == 'zmo-medium' %}
             {% if obj.align == 'left' %}
                figure-horizontal
            {% elif obj.align == 'right' %}
                figure-horizontal--right
            {% else %}
                figure is-constrained is-centered
            {% endif %}
        {% elif obj.layout == 'small' %}
            {% if obj.align == 'right' %}
                figure-stamp--right
            {% else %}
                figure-stamp
            {% endif %}
        {% endif %}
        ">
            <img class="figure__media" src="{{obj.src | default('http://placehold.it/160x90', true)}}">
            <figcaption class="figure__caption">
                {{obj.caption}}
                {{obj.copyright}}
            </figcaption>
    </figure>
{%- endmacro %}

{% macro head_image_longform(obj) -%}
    <div class="article__main-image--longform" style="background-image: url({{obj.src | default('http://placehold.it/160x90', true)}})";>{{obj.caption}}{{obj.copyright}}
    </div>
{%- endmacro %}

{% macro meta_author(author) -%}
    {% if author -%}
        {{ author.prefix }}{{ authorlink(author) }}{{ author.suffix }}
    {%- endif %}
{%- endmacro %}

{% macro authorlink(author, class="article__meta__author") -%}
    {% if author.href -%}
        <a href="{{author.href|translate_url}}" class="{{class}} meta-link">{{author.name}}</a>
    {%- else -%}
        <span class="{{class}}">{{author.name}}</span>
    {%- endif %}
{%- endmacro %}

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
    {% if obj.id -%}
        <figure class="
        {% if obj.format == 'small' %}
            figure-stamp
        {% elif obj.format == 'large' %}
            figure-full-width
        {% elif obj.format == 'small-right' %}
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

{% macro comment(indented, img_url, name, timestamp, role, text) -%}
    <article class="comment {% if indented -%}is-indented{%- endif %}">
        <div class="comment__head">
            {% if img_url -%}
                <img src="{{img_url}}" class="comment__head__img" />
            {%- endif %}
            <div class="comment__head__meta">
                <strong class="comment__head__meta__name">{{name}}</strong>
                <a href="#" class="comment__head__meta__date">{{timestamp}}</a>
                {% if role -%}
                    <div class="comment__head__meta__label">{{role}}</div>
                {%- endif %}
            </div>
        </div>
        <div class="comment__body">
            <p>{{text|safe}}</p>
        </div>
        <aside class="comment__tools">
            <a class="comment__tools__flag icon-flag">Kommentar melden</a>
            <a class="comment__tools__reply icon-reply">Auf Kommentar antworten</a>
        </aside>
    </article>
{%- endmacro %}

{% macro mock_comments(comments) -%}
    <div class="tc">
        <div class="article__comments-trigger" id="js-comments-trigger">
            <div class="article__comments-trigger__wrap">
                <span class="article__comments-trigger__count icon-close-comments">47</span>
                Kommentare
            </div>
        </div>
    </div>
    <section class="comments" id="js-comments">
        <div class="comments__head" id="js-comments-head">
            <form class="comments__head__form" id="js-comments-head-form">
                <textarea placeholder="Ich denke …"></textarea>
                <input type="submit" class="button" value="Kommentieren" />
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
                        {% for commentdict in comments %}
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
{%- endmacro %}
