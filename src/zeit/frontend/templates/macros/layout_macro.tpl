
{% macro ga_tracking() -%}
<!-- ga tracking -->
        <script type="text/javascript">
            var _gaq = _gaq || [];
            _gaq.push(['_setAccount', 'UA-18122964-1']);
            _gaq.push(['_setDomainName', '.zeit.de']);
            _gaq.push (['_gat._anonymizeIp']);
            _gaq.push(['_trackPageview']);
            (function() {
            var ga = document.createElement('script');
            ga.type = 'text/javascript';
            ga.async = true;
            ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
            var s = document.getElementsByTagName('script')[0];
            s.parentNode.insertBefore(ga, s); })();
        </script>
{%- endmacro %}

{% macro cc_tracking(channel) -%}
<!-- cc tracking -->
    <script type="text/javascript">
        document.write('<img alt="" class="visuallyhidden" src="http://cc.zeit.de/cc.gif?banner-channel={{channel}}&r='+escape(document.referrer)+'&rand='+Math.random()*10000000000000000+'">');
    </script>
{%- endmacro %}

{% macro meetrics_tracking() -%}
<!-- meetrics tracking -->
    <script type="text/javascript" src="http://scripts.zeit.de/js/rsa.js"></script>
    <script type="text/javascript">try{loadMWA208571();}catch(e){}</script>
    <script type="text/javascript">try{mainMWA208571();}catch(e){}</script>
{%- endmacro %}

{% macro webtrekk_tracking(obj, request) -%}
<!-- webtrekk tracking -->
        <script type="text/javascript" src="http://scripts.zeit.de/static/js/webtrekk/webtrekk_v3.js"></script>
        <script type="text/javascript">

            var Z_WT_KENNUNG =
            "redaktion.{{obj.ressort}}.{{obj.sub_ressort}}..{{obj.type}}.online.{{request.path_info}}"; // content id

            var webtrekk = {
                linkTrack : "standard",
                heatmap : "0",
                linkTrackAttribute: "id"
            };

            var wt = new webtrekkV3(webtrekk);

            wt.cookie = "1"; // (3|1, 1st or 3rd party cookie)
            wt.contentGroup = {
                1: "Redaktion",
                2: "{{obj.tracking_type}}",
                3: "{{obj.ressort}}",
                4: "Online"
            };

            {% if obj.type == 'article' -%}
                wt.customParameter = {
                    1: "{% if obj.author %}{{obj.author.name}}{% endif %}",
                    2: "{{obj.banner_channel}}",
                    3: "1/1",
                    4: "{{obj.rankedTagsList}}",
                    6: "{{obj.text_length}}",
                    7: "",
                    9: "{{obj.banner_channel}}"
                };
             {%- endif %}

            wt.contentId = Z_WT_KENNUNG;
            wt.sendinfo();
        </script>
        <noscript>
            <div><img alt="" width="1" height="1"
            src="http://zeit01.webtrekk.net/981949533494636/wt.pl?p=311,redaktion.{{obj.ressort}}.{{obj.sub_ressort}}..{{obj.tracking_type}}.online.{{request.path_info}},0,0,0,0,0,0,0,0&amp;cg1=Redaktion&amp;cg2={{obj.tracking_type}}&amp;cg3={{obj.ressort}}&amp;cg4=Online&amp;cp1={% if obj.author %}{{obj.author.name}}{% endif %}&amp;cp2={{obj.banner_channel}}&amp;cp3=1&amp;cp4={{obj.rankedTagsList}}&amp;cp6={{obj.text_length}}&amp;cp7=&amp;cp9={{obj.banner_channel}}"></div>
        </noscript>
{%- endmacro %}

{% macro date_meta(view) -%}
    {% if view.date_last_published_semantic %}
        <meta name="last-modified" content="{{ view.date_last_published_semantic }}"/>
        <meta http-equiv="last-modified" content="{{ view.date_last_published_semantic }}"/>
    {% else %}
        <meta name="last-modified" content="{{ view.date_first_released_meta }}"/>
        <meta http-equiv="last-modified" content="{{ view.date_first_released_meta }}"/>
    {% endif %}
    <meta name="date" content="{{ view.date_first_released_meta }}"/>
{%- endmacro %}
{% macro breadcrumbs(crumbs) -%}
    <div class="breadcrumbs-wrap">
        <div class="breadcrumbs" id="js-breadcrumbs">
            <div class="breadcrumbs__list-wrap">
                <div class="breadcrumbs__list">
                    {% for crumb in crumbs %}
                        <div class="breadcrumbs__list__item" itemscope="itemscope" itemtype="http://data-vocabulary.org/Breadcrumb">
                            <a href="{{crumb[1]}}" itemprop="url">
                                <span itemprop="title">{{crumb[0]}}</span>
                            </a>
                        </div>
                        {% if not loop.last %}
                          &rsaquo;
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
{%- endmacro %}

{% macro sharing_meta(obj,request) -%}
    <meta name="twitter:card" content="{{obj.twitter_card_type}}">
    <meta name="twitter:site" content="@zeitonline">
    <meta name="twitter:creator" content="@zeitonline">
    <meta name="twitter:title" content="{{obj.title}}">
    <meta name="twitter:description" content="{{obj.subtitle}}">
    <meta property="og:site_name" content="ZEIT ONLINE">
    <meta property="fb:admins" content="595098294">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{{obj.title}}">
    <meta property="og:description" itemprop="description" content="{{obj.subtitle}}">
    <meta property="og:url" content="{{request.host}}{{request.path_info}}">

    {% if obj.sharing_img %}
        {% if obj.sharing_img.video_still %}
            <meta property="og:image" content="{{obj.sharing_img.video_still}}">
            <link itemprop="image" rel="image_src" href="{{obj.sharing_img.video_still}}">
            <meta name="twitter:image" content="{{obj.sharing_img.video_still}}">
        {% else %}
            <meta property="og:image" class="scaled-image" content="{{obj.sharing_img | default_image_url |  default('http://placehold.it/160x90', true)}}">
            <link itemprop="image" class="scaled-image" rel="image_src" href="{{obj.sharing_img | default_image_url | translate_url | default('http://placehold.it/160x90', true)}}">
            <meta class="scaled-image" name="twitter:image" content="{{obj.sharing_img | default_image_url | default('http://placehold.it/160x90', true)}}">
        {% endif %}
    {% endif %}
{%- endmacro %}

{% macro iqd_init() -%}
<script type="text/javascript">
    // negative keyword 'diuqilon'
    // todo: if we get a billboard, we need more options (NB)
    var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    window.diuqilon = (w < 1024) ? ',diuqilon' : '';
    // IQD varPack
    window.IQD_varPack = {
        iqdSite: 'zol',
        iqdRessort: '',
        ord: Math.random()*10000000000000000,
        iqdSiteInfo: [[980, 0, 0], [0, 0, 980], [0, 0, 980], ['center', 'fullBodyBg'], ['y', 'y', 'y']],
        iqdCountSkyReq: parseInt(0,10),
        iqdEnableSky: 'neutral'
    };
    // IQD variable test
    window.iqd_Loc = (window.top===window.self) ? window.location : parent.location;
    window.iqd_Domain = window.iqd_Loc.href.toLowerCase();
    window.iqd_TestKW = (window.iqd_Domain.indexOf('iqadtest=true')> -1) ? 'iqadtest' : 'iqlive';
    // ]]>
</script>
{%- endmacro %}

{% macro iqd_krux_head() -%}
<script type="text/javascript" src="http://ad.yieldlab.net/yp/21752,21754,21759,21987?ts=1392992264"></script>
{# BEGIN Krux Control Tag for "IQ" #}
{# Source: /snippet/controltag?confid=Ip52Cnbc&site=IQ&edit=1 #}
<script class="kxct" data-id="Ip52Cnbc" data-timing="async" data-version="1.9" type="text/javascript">
    window.Krux||((Krux=function(){Krux.q.push(arguments)}).q=[]);
    (function(){
        var k=document.createElement('script');k.type='text/javascript';k.async=true;
        var m,src=(m=location.href.match(/\bkxsrc=([^&]+)/))&&decodeURIComponent(m[1]);
        k.src = /^https?:\/\/([^\/]+\.)?krxd\.net(:\d{1,5})?\//i.test(src) ? src : src === "disable" ? "" : (location.protocol==="https:"?"https:":"http:")+"//cdn.krxd.net/controltag?confid=Ip52Cnbc";
        var s=document.getElementsByTagName('script')[0];s.parentNode.insertBefore(k,s);
    }());
</script>
{# END Krux Controltag #}
{# BEGIN Krux IQ #}
<script class="kxint" type="text/javascript">
    window.Krux||((Krux=function(){Krux.q.push(arguments);}).q=[]);
    (function(){
        var Krux = this.Krux.adaudience = this.Krux.adaudience || {};
        function retrieve(n){
            var m, k='kxadaudience_'+n;
            if (window.localStorage) {
                return window.localStorage[k] || "";
            } else if (navigator.cookieEnabled) {
                m = document.cookie.match(k+'=([^;]*)');
                return (m && unescape(m[1])) || "";
            } else {
                return '';
            }
        }
        Krux.user = retrieve('user');
        Krux.segments = retrieve('segs') ? retrieve('segs').split(',') : [];
        var dfpp = [];
        for(var i = 0; i < Krux.segments.length; i++) {
            dfpp.push(Krux.segments[i]);
        }
        Krux.dfppKeyValues = dfpp.length ? dfpp.join(',') + ';' : '';
        Krux.dfppKeyValues = 'ksg=' + Krux.dfppKeyValues;
    })();
</script>
{%- endmacro %}

{% macro main_nav(is_full_width) -%}
    <nav class="main-nav has-hover {% if is_full_width %}is-full-width{% endif %}" id="js-main-nav" itemscope itemtype="http://schema.org/SiteNavigationElement">
        <div class="main-nav__wrap">
            <a href="http://zeit.de/zeit-magazin/index" class="main-nav__logo" itemscope itemtype="http://schema.org/Organization">
                <meta itemprop="name" content="Zeit Online">
                <div class="main-nav__logo__wrap">
                    <span class="main-nav__logo__img icon-zm-logo--white" itemprop="logo" title="ZEIT ONLINE" alt="Nachrichten auf ZEIT ONLINE"></span>
                </div>
            </a>
            <div class="main-nav__menu">
                <header class="main-nav__menu__head" id="js-main-nav-trigger">
                    <div class="main-nav__menu__head__headline"></div>
                    <div class="main-nav__menu__head__hamburger">Menu Öffnen</div>
                </header>
                <div class="main-nav__menu__content" id="js-main-nav-content">
                    <div class="main-nav__section main-nav__ressorts">
                        <div class="main-nav__section__content is-always-open" id="js-main-nav-ressorts-slider-container">
                            <div class="main-nav__ressorts__slider-arrow--left icon-arrow-left is-inactive"></div>
                            <div class="main-nav__ressorts__slider-arrow--right icon-arrow-right"></div>
                            <div class="main-nav__section__content__wrap" id="js-main-nav-ressorts-slider-strip">
                                <a href="http://{{request.host}}/zeit-magazin/mode-design/index">Mode & Design</a>
                                <a href="http://{{request.host}}/zeit-magazin/essen-trinken/index">Essen & Trinken</a>
                                <a href="http://{{request.host}}/zeit-magazin/leben/index">Leben</a>
                            </div>
                        </div>
                    </div>
                    <div class="main-nav__section main-nav__all-ressorts">
                        <a href="http://www.zeit.de/index"
                        class="is-standalone-link">» ZEIT ONLINE</a>
                    </div>
                    <div class="main-nav__section main-nav__service-primary">
                        <div class="main-nav__section__content is-always-open">
                            <a href="http://www.zeitabo.de/?mcwt=2009_07_0002">Abo</a>
                            <a href="http://shop.zeit.de/?et=l6VVNm&et_cid=42&et_lid=175&et_sub=Startseite_header">Shop</a>
                            <a href="https://premium.zeit.de/?wt_mc=pm.intern.fix.zeitde.fix.dach.text.epaper">ePaper</a>
                        </div>
                    </div>
                    <div class="main-nav__section main-nav__service">
                        <span class="main-nav__section__trigger icon-arrow-down">Service</span>
                        <div class="main-nav__section__content">
                            <div class="main-nav__section__content__wrap">
                                <a href="http://www.zeit.de/campus/index">ZEITCampus</a>
                                <a href="http://www.zeit.de/wissen/zeit-geschichte/index">ZEITGeschichte</a>
                                <a href="http://www.zeit.de/wissen/zeit-wissen/index">ZEITWissen</a>
                                <a href="http://www.zeit.de/angebote/partnersuche/index?pscode=01_100_20003_0001_0001_0005_empty_AF00ID_GV00ID">Partnersuche</a>
                                <a href="http://zeit.immowelt.de/">Immobilien</a>
                                <a href="http://automarkt.zeit.de/">Automarkt</a>
                                <a href="http://jobs.zeit.de/">Jobs</a>
                                <a href="https://premium.zeit.de/abo/appsios?wt_mc=pm.intern.fix.zeitde.fix.dach.text.apps">Apps</a>
                                <a href="https://premium.zeit.de/abo/digitalpaket5?wt_mc=pm.intern.fix.zeitde.fix.dach.text.audio">Audio</a>
                                <a href="http://www.zeit.de/archiv">Archiv</a>
                                <a href="http://www.zeit.de/spiele/index">Spiele</a>
                            </div>
                        </div>
                    </div>
                    <!-- <div class="main-nav__section main-nav__search">
                        <span class="main-nav__section__trigger icon-search">Suche</span>
                        <div class="main-nav__section__content">
                            <div class="main-nav__search__form">
                                <input class="main-nav__search__input" type="text" size="20" placeholder="Suchbegriff …">
                                <input class="main-nav__search__submit" type="submit" value="Suchen">
                            </div>
                        </div>
                    </div> -->
                    <div class="main-nav__section main-nav__community">
                        {% if request.app_info.authenticated %}
                            {{ head_user_is_logged_in_true() }}
                        {%- else -%}
                            {{ head_user_is_logged_in_false() }}
                        {%- endif -%}
                    </div>
                </div>
            </div>
        </div>
    </nav>
{%- endmacro %}

{% macro head_user_is_logged_in_true()  %}
    <span class="main-nav__section__trigger main-nav__community--logged-in">
        {% if request.app_info.user.picture %}
            <img src="{{ request.app_info.community_host }}{{ request.app_info.user.picture }}" class="main-nav__community__avatar">
        {%- else -%}
            <span>X</span> <!-- ToDo(T.B.) - Dummycode, tbd by frontend (see https://zeit-online.atlassian.net/browse/ZMO-580#comment-24209) -->
        {%- endif -%}
        Community
    </span>
    <div class="main-nav__section__content">
        <a href="{{ request.app_info.community_host }}user/{{ request.app_info.user.uid }}">Account</a>
        <a href="{{ request.app_info.community_host }}{{ request.app_info.community_paths.logout }}?destination={{ request.url }}">Logout</a>
    </div>
{%- endmacro %}

{% macro head_user_is_logged_in_false()  %}
    <span class="main-nav__section__trigger main-nav__community--logged-out">
        <a href="{{ request.app_info.community_host }}{{ request.app_info.community_paths.login }}?destination={{ request.url }}">Anmelden</a>/
        <a href="{{ request.app_info.community_host }}{{ request.app_info.community_paths.register }}?destination={{ request.url }}">Registrieren</a>
    </span>
{%- endmacro %}

{% macro ivw_ver1_tracking(channel) -%}
<!-- ivw ver1 tracking -->
<!-- SZM VERSION="1.5" -->
<!--Dieses Online-Angebot unterliegt nicht der IVW-Kontrolle!-->
    <script type="text/javascript">
        var Z_IVW_RESSORT = "{{channel}}";
        var IVW="http://zeitonl.ivwbox.de/cgi-bin/ivw/CP/{{channel}}";
        document.write("<img src=\""+IVW+"?r="+escape(document.referrer)+"&d="+(Math.random()*100000)+"\" alt=\"\" width=\"1\" height=\"1\" />");
    </script>
    <noscript>
        <img alt="" src="http://zeitonl.ivwbox.de/cgi-bin/ivw/CP/{{channel}};" height="1" width="1" />
    </noscript>
{%- endmacro %}

{% macro ivw_ver2_tracking(obj,request) -%}
<!-- ivw ver2 tracking -->
<!-- SZM VERSION="2" -->
    <script type="text/javascript">

        //set breakpoint for mobile tracking
        ivw_min_width = 767;

        var iam_data = {
            "st" : "",
            "cp" : "{%if obj.ressort%}{{obj.ressort}}/{%endif%}{%if obj.sub_ressort%}{{obj.sub_ressort}}/{%endif%}bild-text",
            "sv" : "ke",
            "co" : "URL: {{request.path_info}}"
        };

        if( window.innerWidth >= ivw_min_width ){
        //desktop
            iam_data.st = "zeitonl";
        }else{
        //mobile
           iam_data.st = "mobzeit";
        }

        iom.c(iam_data,1);
    </script>
{%- endmacro %}

{% macro iqd_nuggad() -%}
<script type="text/javascript">
    var n_pbt = "";
    nuggtg = encodeURIComponent(IVW.split("CP/")[1]);
    document.write('<scr'+'ipt type="text/javascript" src="http://gwp.nuggad.net/rc?nuggn=223088769&nuggsid=4168690&nuggtg='+nuggtg+'"><\/scr'+'ipt>');
</script>
{%- endmacro %}

{% macro iqd_krux_body() -%}
<script type="text/javascript">
    // <![CDATA[
    var YLP = yl.YpResult || "";
    var ylpid = [21752, 21754, 21759, 21987];
    var ylpid2 = [6069, 3039, 5641, 8504];
    try { var ylpsky = YLP.get(ylpid[0]).id; } catch(e) { ylpsky = 0; }
    try { var ylpmedrec = YLP.get(ylpid[1]).id; } catch(e) { ylpmedrec = 0; }
    try { var ylpsuba = YLP.get(ylpid[2]).id; } catch(e) { ylpsuba = 0; }
    try { var ylpdynamic = YLP.get(ylpid[3]).id; } catch(e) { ylpdynamic = 0; }
    try { var ylpwf = YLP.get(ylpid[3]).format; } catch(e) { ylpwf = 0; }
    var ylpwfid = 'y' + ylpwf;
    var iqd_wlCus = ['ysky', 'ymdr', 'ysba', 'ydyc', ylpwfid];
    var iqd_wlCusRec = [ylpsky, ylpmedrec, ylpsuba, ylpdynamic, ylpwf];
    var iqd_wlCusRecStr = [];
    for (var i = 0; i < iqd_wlCus.length; i++) {
        iqd_wlCusRecStr[i] =  (iqd_wlCusRec[i] > 0) ? iqd_wlCus[i] + '=1' : iqd_wlCus[i] + '=0';
    }
    document.write('<scr'+'ipt>n_pbt += iqd_wlCusRecStr.join("\;");</scr'+'ipt>');
    if (window.Krux.adaudience.dfppKeyValues){
        document.write('<scr'+'ipt>n_pbt += ";" + window.Krux.adaudience.dfppKeyValues;</scr'+'ipt>');
    }
    // ]]>
</script>
<script>n_pbt = n_pbt.substr(0,1150);</script>
{%- endmacro %}

{% macro main_footer() -%}
    <footer class="main-footer">
        <div class="main-footer__box is-constrained is-centered">
            <div class="main-footer__ZM">
                <span class="main-footer__ZM__img icon-zm-logo--white"></span>
            </div>
            <div class="main-footer__links">
                <div>
                    <ul>
                        <li>VERLAG</li>
                        <li><a href="http://www.zeit-verlagsgruppe.de/anzeigen/">Mediadaten</a></li>
                        <li><a href="http://www.zeitverlag.de/presse/rechte-und-lizenzen">Rechte &amp; Lizenzen</a></li>
                    </ul>
                </div>
                <div>
                    <ul>
                        <li>Bildrechte</li>
                        <li><a href="http://www.zeit.de/hilfe/datenschutz">Datenschutz</a></li>
                        <li><a href="http://www.iqm.de/Medien/Online/nutzungsbasierte_onlinewerbung.html">Cookies</a></li>
                        <li><a href="http://www.zeit.de/administratives/agb-kommentare-artikel">AGB</a></li>
                        <li><a href="http://www.zeit.de/impressum/index">Impressum</a></li>
                        <li><a href="http://www.zeit.de/hilfe/hilfe">Hilfe/ Kontakt</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </footer>
{%- endmacro %}

{% macro adplace(banner, pagetype='article') -%}
    {%set kw = 'zeitonline,zeitmz' %}
    <!-- Bannerplatz: "{{banner.name}}", Tile: {{banner.tile}} -->
    <div id="iqadtile{{banner.tile}}" class="ad__{{banner.name}} ad__on__{{pagetype}} ad__width_{{banner.noscript_width_height[0]}} ad__min__{{banner.min_width}}">
        {% if banner.label -%}
        <div class="ad__{{banner.name}}__label">{{ banner.label }}</div>
        {%- endif %}
        <div class="ad__{{banner.name}}__inner">
            <script type="text/javascript">
                if( window.zmo_actual_load_width > {{ banner.min_width|default(0) }} ) {
                document.write('<script src="http://ad.de.doubleclick.net/adj/zeitonline/zolmz;dcopt={{banner.dcopt}};tile={{banner.tile}};' + n_pbt + ';sz={{ banner.sizes|join(',') }};kw=iqadtile{{banner.tile}},{{kw}},'+ iqd_TestKW + {% if banner.diuqilon -%}window.diuqilon{%- else -%}''{%- endif %} + ';ord=' + IQD_varPack.ord + '?" type="text/javascript"><\/script>');
                }
            </script>
            <noscript>
            <div>
                <a href="http://ad.de.doubleclick.net/jump/zeitonline/zolmz;tile={{banner.tile}};sz={{ banner.sizes|join(',') }};kw=iqadtile{{banner.tile}},{{kw}};ord=123456789?" rel="nofollow">
                    <img src="http://ad.de.doubleclick.net/ad/zeitonline/zolmz;tile={{banner.tile}};sz={{ banner.sizes|join(',') }};kw={{banner.tile}},{{kw}};ord=123456789?" width="{{ banner.noscript_width_height[0] }}" height="{{banner.noscript_width_height[1]}}" alt="">
            </a></div>
            </noscript>
        </div>
    </div>
{%- endmacro %}

{% macro main_nav_compact(obj,request) -%}
    <nav class="main-nav is-full-width is-compact" itemscope itemtype="http://schema.org/SiteNavigationElement">
        <div class="main-nav__wrap">
            <a href="http://www.zeit.de" class="main-nav__logo" itemscope itemtype="http://schema.org/Organization">
                <meta itemprop="name" content="Zeit Online">
                <div class="main-nav__logo__wrap">
                    <span class="main-nav__logo__img icon-zm-logo--white" itemprop="logo" title="Nachrichten auf ZEIT ONLINE" alt="Nachrichten auf ZEIT ONLINE" />
                </div>
            </a>
            <div class="main-nav__menu">
                <aside class="main-nav__sharing scaled-image">
                    <a
                    href="http://twitter.com/home?status={{request.host}}{{request.path_info}}" target="_blank" class="main-nav__sharing__item js-has-popup icon-twitter" data-width="600" data-height="300">Auf Twitter teilen</a>

                    {%- if obj.sharing_img.video_still -%}
                        <a
                        href="http://www.facebook.com/sharer/sharer.php?s=100&p[url]={{request.host}}{{request.path_info}}&p[images][0]={{obj.sharing_img.video_still}}&p[title]={{obj.title}}&p[summary]={{obj.subtitle}}" target="_blank" class="main-nav__sharing__item js-has-popup icon-facebook" data-width="600" data-height="300">Auf Facebook teilen</a>
                    {%- else -%}
                        <a
                        href="http://www.facebook.com/sharer/sharer.php?s=100&p[url]={{request.host}}{{request.path_info}}&p[images][0]={{obj.sharing_img | default_image_url | default('http://placehold.it/160x90', true)}}&p[title]={{obj.title}}&p[summary]={{obj.subtitle}}" target="_blank" class="main-nav__sharing__item js-has-popup icon-facebook" data-width="600" data-height="300">Auf Facebook teilen</a>
                    {%- endif -%}

                    <a
                    href="https://plus.google.com/share?url={{request.host}}{{request.path_info}}" target="_blank" class="main-nav__sharing__item js-has-popup icon-google" data-width="480" data-height="350">Auf Google+ teilen</a>
                </aside>
            </div>
        </div>
    </nav>

{%- endmacro %}

{% macro insert_responsive_image(image, image_class) %}
    
    {% set alt = ''%}
    {% set title = ''%}

    {% if image.alt %}
        {% set alt = image.alt %}
        {% set title = image.title %}
    {% elif image.attr_alt %}
        {% set alt = image.attr_alt %}
        {% set title = image.attr_title %}
    {% endif %}
    
    <!--[if gt IE 9]>-->
        <noscript data-ratio="{{image.ratio}}">
    <!--<![endif]-->
            <img {% if alt %}alt="{{alt}}"{% endif %}{% if title %} title="{{title}}" {% endif %}class="{{image_class | default('')}} figure__media" src="{{image | default_image_url | default('http://placehold.it/160x90', true)}}" data-ratio="{{image.ratio}}">
    <!--[if gt IE 9]>-->
        </noscript>
    <!--<![endif]-->
{% endmacro %}
