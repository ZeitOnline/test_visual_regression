<!DOCTYPE html>
<!--[if lt IE 7]> <html lang="de" class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]> <html lang="de" class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]> <html lang="de" class="no-js lt-ie9"> <![endif]-->
<!--[if IE 9]> <html lang="de" class="no-js lt-ie10"> <![endif]-->
<!--[if gt IE 9]><!--> <html lang="de" class="no-js"> <!--<![endif]-->
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" id="viewport-meta">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    {% block css_lte_8_link %}
    <!--[if lte IE 8]>
        <link href="{{ request.asset_host }}/css/web.site/all-old-ie.css" media="screen" rel="stylesheet" type="text/css">
    <![endif]-->
    {% endblock css_lte_8_link %}

    {% block css_link %}
    <!--[if gt IE 8]><!-->
        {% if view.is_advertorial %}
            <link href="{{ request.asset_host }}/css/web.site/advertorial.css" media="screen" rel="stylesheet" type="text/css" />
        {% else %}
            <link href="{{ request.asset_host }}/css/web.site/{{ 'unresponsive' if view.desktop_only else 'screen'}}.css" media="screen" rel="stylesheet" type="text/css">
        {% endif %}
    <!--<![endif]-->
    {% endblock css_link %}

    {% block css_lte9_navi_link %}
    <!--[if lte IE 9]>
        <link href="{{ request.asset_host }}/css/web.site/ie-navi.css" media="screen" rel="stylesheet" type="text/css">
    <![endif]-->
    {% endblock css_lte9_navi_link %}

    {% include "zeit.web.core:templates/inc/inline_js/library.html" ignore missing %}

    {# Modernizr -#}
    <script src="{{ request.asset_host }}/js/vendor/modernizr-custom.js"></script>
    <noscript>
        <link href="{{ request.asset_host }}/css/icons/site.fallback.css" rel="stylesheet">
    </noscript>
    {% if view.framebuilder_requires_ivw %}
        <!-- IVW -->
        <script src="https://script.ioam.de/iam.js"></script>
    {% endif %}
    {% if toggles('third_party_modules', 'iqd') %}
        {% include "zeit.web.core:templates/inc/ads/head.html" ignore missing %}
        {%- block content_ad_script -%}{%- endblock -%}
    {% endif %}
    {% if settings('livereload') %}
        <script src="//localhost:35729/livereload.js"></script>
    {% endif %}
