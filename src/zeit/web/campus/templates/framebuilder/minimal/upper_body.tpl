</head>
<body data-page-type="{{ view.type }}">

    {% include "zeit.web.core:templates/inc/tag-manager.html" %}
    {% include "zeit.web.core:templates/inc/ads/static_oop-tag.html" %}

    {% if view.framebuilder_requires_ivw %}
        {% include "zeit.web.core:templates/inc/tracking/ivw_ver2.html" %}
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
            <header class="header">
                {%- block navigation -%}
                    {%- include "zeit.web.campus:templates/framebuilder/navigation.tpl" -%}
                {%- endblock navigation -%}
            </header>
            {% block adplace_billboard %}
                {# desktop ad place 3 #}
                {{ lama.adplace(view.banner(3), view) }}
                {# mobile ad place 1 #}
                {{ lama.adplace(view.banner(1), view, mobile=True) }}
            {% endblock adplace_billboard %}
            <main class="{{ 'main' | with_mods(view.type) }}" id="main" itemprop="mainContentOfPage">
