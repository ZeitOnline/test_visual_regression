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

{% macro main_nav_compact() -%}
    <nav class="main-nav is-full-width is-compact" itemscope itemtype="http://schema.org/SiteNavigationElement">
        <div class="main-nav__wrap">
            <a href="http://zeit.de" class="main-nav__logo" itemscope itemtype="http://schema.org/Organization">
                <meta itemprop="name" content="Zeit Online">
                <div class="main-nav__logo__wrap">
                    <img src="/img/zeit-logo--magazin.png" class="main-nav__logo__img" itemprop="logo" title="Nachrichten auf ZEIT ONLINE" alt="Nachrichten auf ZEIT ONLINE" />
                </div>
            </a>
            <div class="main-nav__menu">
                <aside class="main-nav__sharing">
                    <a href="http://twitter.com/home?status=Zeit.de" target="_blank" class="main-nav__sharing__item js-has-popup icon-twitter" data-width="600" data-height="300">Auf Twitter teilen</a><a href="http://www.facebook.com/sharer/sharer.php?s=100&p[url]=http://zeit.de&p[images][0]=&p[title]=Zeit.de&p[summary]=" target="_blank" class="main-nav__sharing__item js-has-popup icon-facebook" data-width="600" data-height="300">Auf Facebook teilen</a><a href="https://plus.google.com/share?url=http://zeit.de" target="_blank" class="main-nav__sharing__item js-has-popup icon-google" data-width="480" data-height="350">Auf Google+ teilen</a>
                </aside>
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
            <div class="scaled-image">
                <noscript>
                        <img class="figure__media" src="{{obj | default_image_url | translate_url | default('http://placehold.it/160x90', true)}}" data-ratio="{{obj.ratio}}">
                </noscript>
            </div>
            <figcaption class="figure__caption">
                {{obj.caption}}
                {{obj.copyright}}
            </figcaption>
    </figure>
{%- endmacro %}

{% macro headerimage(obj) -%}
    <div class="scaled-image is-pixelperfect">
        <noscript>
            <img class="article__main-image--longform" src="{{obj | default_image_url | translate_url | default('http://placehold.it/160x90', true)}}">
        </noscript>
    </div>{{obj.caption}}{{obj.copyright}}
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
    {% if obj.id and obj.format != 'zmo-xl-header' -%}
        <figure class="
        {% if obj.format == 'zmo-small' %}
            figure-stamp
        {% elif obj.format == 'zmo-large' %}
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
    <div data-backgroundvideo="true" class="article__main-video--longform"> 
        <video preload="auto" autoplay="true" loop="loop" muted="muted" volume="0" poster="{{obj.video_still}}">
                <source src="{{obj.source}}" type="video/mp4">
                <img class="article__main-image--longform" style="background-image:url({{obj.video_still}})">
        </video>
            <div class="article__main-image--longform video--fallback" style="background-image:url({{obj.video_still}})"></div>
    </div>
{%- endmacro %}

{% macro comment(indented, img_url, name, min_ago, role, text) -%}
    <article class="comment {% if indented -%}is-indented{%- endif %}">
        <div class="comment__head">
            {% if img_url -%}
                <img src="{{img_url}}" class="comment__head__img" />
            {%- endif %}
            <div class="comment__head__meta">
                <strong class="comment__head__meta__name">{{name}}</strong>
                <a href="#" class="comment__head__meta__date">vor {{min_ago}} Minuten</a>
                {% if role -%}
                    <div class="comment__head__meta__label">{{role}}</div>
                {%- endif %}
            </div>
        </div>
        <div class="comment__body">
            <p>{{text}}</p>
        </div>
        <aside class="comment__tools">
            <a class="comment__tools__flag icon-flag">Kommentar melden</a>
            <a class="comment__tools__reply icon-reply">Auf Kommentar antworten</a>
        </aside>
    </article>
{%- endmacro %}

{% macro mock_comments() -%}
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
                        {{ comment(False, "/img/exner.jpg", "Maria Exner", 2, "Community", "Unter Freunden bedarf es ja auch nicht eines solchen Abkommens..." ) }}
                        {{ comment(False, False, "ImmanuelKant", 5, False, "... wäre es wohl angebracht die Amerikanische Botschaft mit Störsignalen aller Art zu übersähen und vielleicht eine intensiever an Verschlüsselungsalgorithmen zu forschen die man dann am besten der ganzen Welt frei zur Verfügung stellt um den so netten Amerikanern mal ordentlich auf ihren arroganten Schlips zu treten!" ) }}
                        {{ comment(True, False, "Super_Kluk", 3, False, "sollte man die Botschaft schließen und alle rechtlichen Mittel nutzen um die Personen ggf. wegen Spionage einzubuchten. Die dann übrig bleiben sollten acht-kantig rausgeschmissen werden. Oder wie verhalten Sie sich mit einem Gast, der sich unmöglich aufführt?" ) }}
                        {{ comment(True, False, "Freidenker.", 2, "Experte", "Da es nachgewiesen ist das die USA von der Botschaft aus spionieren ist der Botschaftsstatus Null und Nichtig. Laut Wiener Übereinkommen untersteht der Botschaft keinerlei Schutz mehr und darf von deutschen Behörden auf staatsfeindliche und Bedrohende Aktivitäten durchsucht werden.Eine andere Sache ist, wieso man erst nach 6 Monaten gemerkt hat das man einen 5 meter hohen Fernsendemast auf der britischen Botschaft hochgezogen hat." ) }}
                        {{ comment(False, False, "michael29821", 10, False, "Ein Völkerrechtler hat neulich im Interview gesagt, das Teile des Besatzungsstatut immer noch in Kraft sind und die USA berechtigt sind uns zu Überwachen. Die Regelungen sind in den Pariser Verträgen und den Geheimen 2+4 Verträgen. Also können sie einen Rückzieher machen wie sie wollen. Sie haben Hoheitsrechte in Deutschland." ) }}
                        {{ comment(False, False, "AntonPree", 15, False, "Die USA erklärt also, dass sie Deutschland weiter ausspionieren muss, um eine gewisse Parität herzustellen?! Sarkastisch gesagt: wir sollen nicht ausgegrenzt werden." ) }}
                        {{ comment(False, "http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTIvMDQvMjAvMTYvMDYvNDcvOTQ3L0NocmlzdGlhbl9wb3J0cmFpdF9xdWFkXzEyMDQxMC5qcGciXSxbInAiLCJ0aHVtYiIsIjUwMHg1MDAjIl1d/Christian_portrait_quad_120410.jpg", "dachsus", 20, False, "Vielleicht kommen unsere Regierenden jetzt doch einmal auf den Gedanken, das wir uns selbst einmal die Finder dreckig machen sollten… sprich: Einen eigenen Geheimdienst ausstatten, der in der Lage ist Deutschland und sein Bürger gegen Übergriffe anderer Staaten zu schützen, und ggf. auch selbst zubeißen kann. Die bequeme Haltung, den Amerikanern die Drecksarbeit zu überlassen und sich selbst die Hände in Unschuld zu Waschen ist leider nicht die Lösung." ) }}
                        {{ comment(False, False, "Gerry10", 25, False, "Hören Politiker sich eigentlich noch selbst zu oder haben die den Verstand nur dann und wann eingeschaltet? Das muss man sich auf der Zunge zergehen lassen: Ein Vertrag der das brechen von Grundrechten regulieren soll wird wohl nicht unterschrieben weil die USA keinen Präzedenzfall schaffen wollen! Ich schaffe es nicht darüber nachzudenken weil mein Verstand etweder kapituliert oder mich verlässt." ) }}
                        {{ comment(False, False, "Super_Klug", 30, False, "sollte man die Botschaft schließen und alle rechtlichen Mittel nutzen um die Personen ggf. wegen Spionage einzubuchten. Die dann übrig bleiben sollten acht-kantig rausgeschmissen werden." ) }}
                        {{ comment(True, False, "Buegeleisenverkaeufer", 25, False, "...indem man sich überlegt, wie mächtig der Gast ist. Und dann lässt man solche Halbstarkenphantasien lieber..." ) }}
                        {{ comment(True, False, "bluecheck", 20, False, "Sie haben vollkommen Recht! Leider ist es aber so, dass die USA zwar Gast bei uns sind, ihnen unser Haus aber gehört." ) }}
                        {{ comment(False, False, "nilszbzb", 55, False, "in sonstigen Meldungen: USA verweigern Deutschland No-Nuke-Abkommen" ) }}
                        {{ comment(False, "http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTMvMDgvMjkvMTAvMTMvMzMvOTA4L3BldGVyX3J1ZG9scGguanBnIl0sWyJwIiwidGh1bWIiLCI1MDB4NTAwIyJdXQ/peter_rudolph.jpg", "Klaus Teuber", 60, False, "Ja, wer solche Freunde hat, braucht keine Feinde mehr. Gibt es vielleicht noch ein Plätzchen für Deutschland in der russischen Freihandelszone? Oder kriegen wir es dann auch mit Klitschko zu tun?" ) }}
                        {{ comment(False, False, "AlleZeitenÄndernSich", 65, False, "Bündnispartner? Die verhalten sich anders. Die Manie der Amerikaner seit dem 11.09. alles unter Kontrolle haben zu wollen, wird ihnen international das Genick brechen! Wir als Europäer können uns das eigentlich nicht gefallen lassen. Es ist ihnen egal! Es ist auch egal, dass sie angeordnete Tötungen durch Drohnen vornehmen lassen. Selbstverständlich nicht im eigenen Land! Alles zum Schutz von wem? Und wer hat wirklich die Kontrolle darüber? Wir sind Bündnispartner von diesem Land? Wirklich?" ) }}
                        {{ comment(False, False, "spectator23", 70, False, "Der Guardian hat doch mal eine NSA Spy Map veröffentlicht, da wird Deutschland eindeutig bevorzugt behandelt in Europa." ) }}
                        {{ comment(False, False, "anne129", 75, False, "... unsere Finger sauber sind. Die USA können nahezu uneingeschränkt deutsche Bürger und Organisationen überwachen und ausspionieren. Das wäre deutschen Nachrichtendiensten und dem Verfassungsschutz in diesem Maße nicht gestattet. Es war schon immer an zu nehmen, dass dies weitgehend mit dem Wissen der deutschen Regierung geschieht, und dass diese auch zumindest teilweise in den Genuss dieser Informationen gelangt, die sie selber gar nicht hätte legal erheben können." ) }}
                        {{ comment(False, "http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTMvMDUvMzEvMTQvMjUvMDUvMjI2L2p1bGlhbl9wYW56ZXIuanBnIl0sWyJwIiwidGh1bWIiLCI1MDB4NTAwIyJdXQ/julian-panzer.jpg", "redshrink", 75, False, "... unsere Finger sauber sind. Die USA können nahezu uneingeschränkt deutsche Bürger und Organisationen überwachen und ausspionieren. Das wäre deutschen Nachrichtendiensten und dem Verfassungsschutz in diesem Maße nicht gestattet. Es war schon immer an zu nehmen, dass dies weitgehend mit dem Wissen der deutschen Regierung geschieht, und dass diese auch zumindest teilweise in den Genuss dieser Informationen gelangt, die sie selber gar nicht hätte legal erheben können." ) }}
                        {{ comment(True, False, "Buegeleisenverkaeufer", 30, False, "In Diensten des deutschen Volkes. Es stellt sich nur die Frage, was dann daraus folgt." ) }}
                        {{ comment(False, "http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTIvMDIvMTAvMTUvMjkvMjkvODUzL2R1bnN0ZXIuanBnIl0sWyJwIiwidGh1bWIiLCI1MDB4NTAwIyJdXQ/dunster.jpg", "raybird", 80, False, "Die Wahl ist ja auch durch. Regierung steht." ) }}
                        {{ comment(False, False, "Thomas Haug", 85, False, "Über kurz oder lang (eher lang) wird das Bündnis mit den USA brechen. Hintergrund werden die nicht mehr zu überbrückenden Differenzen im Blick auf die Welt sein." ) }}
                        {{ comment(False, False, "tomtom19582", 90, False, "Zum Einen scheint es im Interesse unserer eigenen Politiker zu sein, auch über unsere Grundrechte hinausgehende Überwachungsmethoden anwenden zu wollen. Ich erinnere hier nur an die Aktivitäten DEUTSCHER Politiker binnen der letzten 25 Jahre, was die Verschärfung der Überwachungsmöglichkeiten anbelangt. Diese Linie wurde von allen Regierungsparteien gleichermaßen Schritt für Schritt verfolgt! (Rot-Grün, Schwarz-Rot, Schwarz-Gelb). Von den im Bundestag vertretenen Parteien waren lediglich die FDP und die Linken nicht damit einverstanden. Die spielen aber die nächsten Jahre vor dem Hintergrund eine GroKo keine Rolle mehr. Zum Zweiten stehen handfeste wirtschaftliche Interessen dahinter, so dass auch die Wirtschaftslobbies sich vehement gegen einen Bruch mit den USA aussprechen werden." ) }}
                        {{ comment(False, False, "DerDoktor", 100, False, "in den Hinterzimmern eigentlich bereits einen Verhandlungsvorteil durch ihr aus der Spionage resultierendes Mehrwissen?" ) }}
                        {{ comment(False, "http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTIvMDIvMTAvMTUvMjkvMTQvOTY4L3Bob3RvXzIxOC5qcGVnIl0sWyJwIiwidGh1bWIiLCI1MDB4NTAwIyJdXQ/photo_218.jpeg", "mugu1", 120, False, "Kommen wir zum 2. Gesicht: Echt überraschend ist m.E., dass nun endlich ein US-Bundesgericht gegen diese maßlose Praxis der NSA der Totalüberwachung vorgegangen ist. Sollte dies Schule machen, steht zumindest i.d. USA diese Form vor dem Aus. Aber natürlich nicht die Praxis an sich. Das Schlupfloch wurde ja gleich mitpräsentiert: So halten dann eben die Telefongesellschaften die Daten zum Abruf bereit. Und trotzdem ist es bemerkenswert, was sich in den USA vor Gericht ereignet hat. Denn für die Zukunft könnte dies der 1. Schritt zurück auf den richtigen Pfad sein. Doch der Rückweg ist lang. Vielleicht gar schon unerreichbar." ) }}

                    </div>
                </div>
                <div class="tabs__content">
                    <a name="tab2"></a>
                    <div class="comments__list">
                        {{ comment(False, "http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTIvMDQvMjAvMTYvMDYvNDcvOTQ3L0NocmlzdGlhbl9wb3J0cmFpdF9xdWFkXzEyMDQxMC5qcGciXSxbInAiLCJ0aHVtYiIsIjUwMHg1MDAjIl1d/Christian_portrait_quad_120410.jpg", "dachsus", 20, False, "Vielleicht kommen unsere Regierenden jetzt doch einmal auf den Gedanken, das wir uns selbst einmal die Finder dreckig machen sollten… sprich: Einen eigenen Geheimdienst ausstatten, der in der Lage ist Deutschland und sein Bürger gegen Übergriffe anderer Staaten zu schützen, und ggf. auch selbst zubeißen kann. Die bequeme Haltung, den Amerikanern die Drecksarbeit zu überlassen und sich selbst die Hände in Unschuld zu Waschen ist leider nicht die Lösung." ) }}
                        {{ comment(False, False, "tomtom19582", 90, False, "Zum Einen scheint es im Interesse unserer eigenen Politiker zu sein, auch über unsere Grundrechte hinausgehende Überwachungsmethoden anwenden zu wollen. Ich erinnere hier nur an die Aktivitäten DEUTSCHER Politiker binnen der letzten 25 Jahre, was die Verschärfung der Überwachungsmöglichkeiten anbelangt. Diese Linie wurde von allen Regierungsparteien gleichermaßen Schritt für Schritt verfolgt! (Rot-Grün, Schwarz-Rot, Schwarz-Gelb). Von den im Bundestag vertretenen Parteien waren lediglich die FDP und die Linken nicht damit einverstanden. Die spielen aber die nächsten Jahre vor dem Hintergrund eine GroKo keine Rolle mehr. Zum Zweiten stehen handfeste wirtschaftliche Interessen dahinter, so dass auch die Wirtschaftslobbies sich vehement gegen einen Bruch mit den USA aussprechen werden." ) }}
                        {{ comment(False, "http://app.resrc.it/s=w350,pd1/o=90/http://staging.espi2013.cloudcontrolled.com/system/images/W1siZiIsIjIwMTIvMDIvMTAvMTUvMjkvMTQvOTY4L3Bob3RvXzIxOC5qcGVnIl0sWyJwIiwidGh1bWIiLCI1MDB4NTAwIyJdXQ/photo_218.jpeg", "mugu1", 120, False, "Kommen wir zum 2. Gesicht: Echt überraschend ist m.E., dass nun endlich ein US-Bundesgericht gegen diese maßlose Praxis der NSA der Totalüberwachung vorgegangen ist. Sollte dies Schule machen, steht zumindest i.d. USA diese Form vor dem Aus. Aber natürlich nicht die Praxis an sich. Das Schlupfloch wurde ja gleich mitpräsentiert: So halten dann eben die Telefongesellschaften die Daten zum Abruf bereit. Und trotzdem ist es bemerkenswert, was sich in den USA vor Gericht ereignet hat. Denn für die Zukunft könnte dies der 1. Schritt zurück auf den richtigen Pfad sein. Doch der Rückweg ist lang. Vielleicht gar schon unerreichbar." ) }}
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
