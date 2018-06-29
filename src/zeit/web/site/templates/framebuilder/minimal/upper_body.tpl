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
                <div class="header__publisher" data-ct-row="lead">
                    <a href="{{ request.route_url('home') }}index" title="Nachrichten auf ZEIT ONLINE" data-ct-label="logo">
                        {{ lama.use_svg_icon('logo-zon-black', 'header__logo', view.package) }}
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
                {% include "zeit.web.core:templates/inc/ads/places/desktop/place3.html" %}
                {# mobile ad place 1 #}
                {% include "zeit.web.core:templates/inc/ads/places/mobile/place1.html" %}
            {% endblock adplace_billboard %}
            <main class="{{ 'main' | with_mods(view.type) }}" id="main">
