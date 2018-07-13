<!DOCTYPE html>
<html lang="de" class="no-js">
<head>
    <meta charset="utf-8">
    <title>ZEIT ONLINE</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" id="viewport-meta">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">

    <link rel="shortcut icon" sizes="16x16 32x32" href="{{ request.asset_host }}/icons/favicon.ico">

    {% block css_link -%}
        {% if view.is_advertorial -%}
            <link href="{{ request.asset_host }}/css/web.site/advertorial.css" media="screen" rel="stylesheet" type="text/css" />
        {%- else -%}
            {# The charset attribute is obsolete in HTML5, but needed for jobs.zeit.de in march 2017. That iso-encoded page does not respect our CSS charset HTTP-header in older browsers, so we need to enforce it here. This should be removed when jobs.zeit.de is modernized or IE9 is dumped. #}
            <link href="{{ request.asset_host }}/css/web.site/{{ 'unresponsive' if view.desktop_only else 'framebuilder'}}.css" media="screen" rel="stylesheet" type="text/css"{% if view.desktop_only %} charset="utf-8"{% endif %}>
        {%- endif %}
    {% endblock css_link -%}

    {% include "zeit.web.core:templates/inc/inline_js/library.html" %}

    {# Modernizr -#}
    <script>{% include "zeit.web.core:templates/inc/inline_js/modernizr-replacement.js" %}</script>
    <script src="{{ request.asset_host }}/js/vendor/modernizr-custom.js"></script>

    {% if view.framebuilder_requires_ivw -%}
        <script src="https://script.ioam.de/iam.js"></script>
    {%- endif %}

    {% if toggles('third_party_modules', 'iqd') -%}
        {% include "zeit.web.core:templates/inc/ads/head.html" %}
    {%- endif %}

    {% if settings('livereload') -%}
        <script src="//localhost:35729/livereload.js"></script>
    {%- endif %}
