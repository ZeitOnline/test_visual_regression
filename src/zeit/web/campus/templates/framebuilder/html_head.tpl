<!DOCTYPE html>
<html lang="de" class="no-js">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" id="viewport-meta">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    {% block css_link %}
    <link href="{{ request.asset_host }}/css/web.campus/screen.css" media="all" rel="stylesheet" type="text/css">
    {% endblock css_link %}
    {%- include "zeit.web.core:templates/inc/inline_js/library.html" -%}

    {# Modernizr -#}
    <script src="{{ request.asset_host }}/js/vendor/modernizr-custom.js"></script>
    {# SVG for Everybody -#}
    <script src="{{ request.asset_host }}/js/vendor/svg4everybody.legacy.js"></script>
    <script>
        {# needed for styling SVG in IE8 #}
        document.createElement( 'svg' );
        svg4everybody({
            fallback: function ( src, svg, use ) {
                return src.replace( /web\.campus\/icons\.svg(\?.+)?#svg-(.+)/ , 'icons/campus/$2.png$1');
            }
        });
    </script>
    {% if view.framebuilder_requires_ivw %}
        <!-- IVW -->
        <script src="https://script.ioam.de/iam.js"></script>
    {% endif %}

    {% if toggles('third_party_modules', 'iqd') %}
        {% include "zeit.web.core:templates/inc/ads/head.html" %}
        {%- block content_ad_script -%}{%- endblock -%}
    {% endif %}
    {% if settings('livereload') %}
        <script src="//localhost:35729/livereload.js"></script>
    {% endif %}
