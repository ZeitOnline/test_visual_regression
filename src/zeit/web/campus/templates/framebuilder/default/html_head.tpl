<!DOCTYPE html>
<html lang="de" class="no-js" itemscope itemtype="http://schema.org/WebPage">
<head>
    <meta charset="utf-8">
    <title>ZEIT ONLINE</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" id="viewport-meta">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    {# XXX: One of the things to clean up once we have SSL/https #}
    <link rel="shortcut icon" sizes="16x16 32x32" href="{{ request.asset_host }}/icons/favicon.ico">
    {% block css_link -%}
        <link href="{{ request.asset_host }}/css/web.campus/framebuilder.css" media="all" rel="stylesheet" type="text/css">
    {%- endblock css_link %}

    {% include "zeit.web.core:templates/inc/inline_js/library.html" %}

    {# Modernizr -#}
    <script src="{{ request.asset_host }}/js/vendor/modernizr-custom.js"></script>
    {% if view.framebuilder_requires_ivw -%}
        <!-- IVW -->
        <script src="https://script.ioam.de/iam.js"></script>
    {%- endif %}

    {% if toggles('third_party_modules', 'iqd') -%}
        {% include "zeit.web.core:templates/inc/ads/head.html" %}
    {%- endif %}

    {% if settings('livereload') -%}
        <script src="//localhost:35729/livereload.js"></script>
    {%- endif %}
