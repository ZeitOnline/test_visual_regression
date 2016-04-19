{% extends 'zeit.web.core:templates/macros/layout_macro.tpl' %}

{% macro playbutton(modifier, duration) %}
    <span class="video-text-playbutton video-text-playbutton--{{ modifier }}">
        <span class="video-text-playbutton__text video-text-playbutton__text--{{ modifier }}">Video ansehen</span><span class="video-text-playbutton__duration">{{ duration }}</span>
    </span>
{% endmacro %}

