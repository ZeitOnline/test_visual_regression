<!DOCTYPE html>
<html lang="de" itemscope itemtype="http://schema.org/WebPage">
<head>
    <meta charset="utf-8">
    <title>ZEIT ONLINE</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" id="viewport-meta">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">

    {% block css_link -%}
        <link href="{{ request.asset_host }}/css/web.site/framebuilder-minimal.css" media="screen" rel="stylesheet" type="text/css">
    {%- endblock css_link %}

    {% include "zeit.web.core:templates/inc/inline_js/library.html" ignore missing %}

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