</head>
<body data-page-type="{{ view.type }}" data-is-hp="{{ view.is_hp | lower }}" data-unique-id="{{ view.context.uniqueId }}" data-ad-delivery-type="{{ view.ad_delivery_type }}"{% if view.is_wrapped %} data-is-wrapped="true"{% endif %}>

    {% include "zeit.web.core:templates/inc/tag-manager.html" %}

    {% include "zeit.web.core:templates/inc/ads/static_oop-tag.html" ignore missing %}

    {% if view.framebuilder_requires_ivw %}
        {% include "zeit.web.core:templates/inc/tracking/ivw_ver2.html" ignore missing %}
    {% endif %}

    {% block skiplink %}
    <a class="skiplink" href="#main" id="top" title="Direkt zum Inhalt springen">Inhalt</a>
    {% endblock skiplink %}

    <div class="page">
        <div class="page__content" {% if view.framebuilder_width %} style="margin: 0 auto; max-width:{{ view.framebuilder_width }};"{% endif %}>
            <header class="header">
                <div class="{{ 'main_nav' | with_mods('has-login' if view.framebuilder_has_login) }}" id="main_nav">
                    <!-- logo -->
                    <div id="publisher" itemprop="publisher" itemscope itemtype="http://schema.org/Organization" class="logo_bar">
                        <div class="logo_bar__brand" itemprop="brand">
                            <a itemprop="url" href="{{ request.route_url('home') }}index" title="Nachrichten auf ZEIT ONLINE" data-id="topnav.2.1..logo">
                                <meta itemprop="name" content="ZEIT ONLINE">
                                <span itemprop="logo" itemscope itemtype="http://schema.org/ImageObject">
                                    {{ lama.use_svg_icon('logo-zon-black', 'logo_bar__brand-logo', view.package) }}
                                    <meta itemprop="url" content="{{ request.asset_host }}/images/structured-data-publisher-logo-zon.png">
                                    <meta itemprop="width" content="235">
                                    <meta itemprop="height" content="25">
                                </span>
                            </a>
                        </div>
                    </div>

                    {% if view.framebuilder_has_login %}
                        <div class="login">
                            <!-- start::cut_mark::login -->
                                <a href="{{ login }}">Anmelden</a>
                            <!-- end::cut_mark::login -->
                        </div>
                    {% endif %}
                </div>
            </header>
            {% block adplace_billboard %}
                {# desktop ad place 3 #}
                {{ lama.adplace(view.banner(3), view) }}
                {# mobile ad place 1 #}
                {{ lama.adplace(view.banner(1), view, mobile=True) }}
            {% endblock adplace_billboard %}
            <main class="{{ 'main' | with_mods(view.type) }}" id="main" itemprop="mainContentOfPage">
