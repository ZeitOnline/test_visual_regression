</head>
<body itemscope itemtype="http://schema.org/WebPage" data-page-type="{{ view.type }}" data-is-hp="{{ view.is_hp | lower }}" data-unique-id="{{ view.context.uniqueId }}" data-ad-delivery-type="{{ view.ad_delivery_type }}"{% if view.is_wrapped %} data-is-wrapped="true"{% endif %}>

    <div class="invisible">
        {% include "zeit.web.static:css/web.site/framebuilder.svg" %}
    </div>

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
        <div class="page__content">
            <header class="header" role="banner">
                {%- include "zeit.web.site:templates/framebuilder/navigation.tpl" ignore missing -%}
            </header>
            {% block adplace_billboard %}
                {# desktop ad place 3 #}
                {{ lama.adplace(view.banner(3), view) }}
                {# mobile ad place 1 #}
                {{ lama.adplace(view.banner(1), view, mobile=True) }}
            {% endblock adplace_billboard %}
            <main class="{{ 'main' | with_mods(view.type) }}" id="main" role="main" itemprop="mainContentOfPage">

            {%- if view.is_advertorial and view.cap_title %}
                <div class="advertorial-marker advertorial-marker--single">
                    <div class="advertorial-marker__label advertorial-marker__label--single">{{ view.cap_title }}</div>
                </div>
            {% endif %}
