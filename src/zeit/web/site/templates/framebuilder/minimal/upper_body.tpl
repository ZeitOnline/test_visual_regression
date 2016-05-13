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
        {% block adplace_top %}
            <div id="iqd_mainAd" >
                <div id="iqd_align_Ad">
                    <div id="iqd_topAd">
                        {{ lama.adplace(view.banner(1), view) }}
                        <div id="iqd_rightAd">
                            {{ lama.adplace(view.banner(2), view) }}
                        </div>
                    </div>
                </div>
            </div>
        {% endblock adplace_top %}
        <div class="page__content" {% if view.framebuilder_width %} style="margin: 0 auto; max-width:{{ view.framebuilder_width }};"{% endif %}>
            <header class="header">
                <div class="main_nav" id="main_nav">
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
                </div>
            </header>
            {% block adplace_billboard %}
                {# desktop ad place 3 #}
                {{ lama.adplace(view.banner(3), view) }}
                {# mobile ad place 1 #}
                {{ lama.adplace(view.banner(1), view, mobile=True) }}
            {% endblock adplace_billboard %}
            <main class="{{ 'main' | with_mods(view.type) }}" id="main" itemprop="mainContentOfPage">

            {%- if view.is_advertorial and view.cap_title %}
                <div class="advertorial-marker advertorial-marker--single">
                    <div class="advertorial-marker__label advertorial-marker__label--single">{{ view.cap_title }}</div>
                </div>
            {% endif %}

<div style="background-color:#D8D8D8;color:#A8A8A8;height:325px;line-height:325px;text-align:center;">TODO: REMOVE DUMMY BOX</div>
