</head>
<body>

    {% include "zeit.web.core:templates/inc/tag-manager.html" %}

    {% include "zeit.web.core:templates/inc/ads/static_oop-tag.html" %}

    {% if view.framebuilder_requires_ivw %}
        {% include "zeit.web.core:templates/inc/tracking/ivw_ver2.html" %}
    {% endif %}

    {% block skiplink -%}
        <a class="skiplink" href="#main" id="top" title="Direkt zum Inhalt springen">Inhalt</a>
    {%- endblock skiplink %}

    <div class="page">
        <div class="page__content" {% if view.framebuilder_width %} style="margin: 0 auto; max-width:{{ view.framebuilder_width }};"{% endif %}>
            <header class="{{ 'header' | with_mods('has-login' if view.framebuilder_has_login) }}" data-ct-area="topnav">
                <!-- logo -->
                <div class="header__publisher" id="publisher" itemprop="publisher" itemscope itemtype="http://schema.org/Organization" data-ct-row="lead">
                    <a itemprop="url" href="{{ request.route_url('home') }}index" title="Nachrichten auf ZEIT ONLINE" data-ct-label="logo">
                        <meta itemprop="name" content="ZEIT ONLINE">
                        <span itemprop="logo" itemscope itemtype="http://schema.org/ImageObject">
                            {{ lama.use_svg_icon('logo-zon-black', 'header__logo', view.package) }}
                            {# The "logo" dimensions must not exceed 600x60 -#}
                            <meta itemprop="url" content="{{ request.asset_host }}/images/structured-data-publisher-logo-zon.png">
                            <meta itemprop="width" content="565">
                            <meta itemprop="height" content="60">
                        </span>
                    </a>
                </div>

                {% if view.framebuilder_has_login %}
                    <div class="header__login" data-ct-row="usermenu">
                        <!-- start::cut_mark::login -->
                            <a href="{{ login }}">Anmelden</a>
                        <!-- end::cut_mark::login -->
                    </div>
                {% endif %}
            </header>
            {% block adplace_billboard %}
                {# desktop ad place 3 #}
                {{ lama.adplace(banner(3), view) }}
                {# mobile ad place 1 #}
                {{ lama.adplace(banner(1), view, mobile=True) }}
            {% endblock adplace_billboard %}
            <main class="{{ 'main' | with_mods(view.type) }}" id="main" itemprop="mainContentOfPage">
