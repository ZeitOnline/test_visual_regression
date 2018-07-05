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
            {% include "zeit.web.core:templates/inc/ads/mainad.html" %}
        {% endblock adplace_top %}
        <div class="page__content">
            <header class="header" data-ct-area="campus-topnav">
                {%- block navigation -%}
                    {%- include "zeit.web.campus:templates/framebuilder/default/navigation.tpl" -%}
                {%- endblock navigation -%}
            </header>
            {% block adplace_billboard %}
                {# desktop ad place 3 #}
                {% include "zeit.web.core:templates/inc/ads/places/desktop/place3.html" %}
                {# mobile ad place 1 #}
                {% include "zeit.web.core:templates/inc/ads/places/mobile/place1.html" %}
            {% endblock adplace_billboard %}
            <main class="{{ 'main' | with_mods(view.type) }}" id="main">
