{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama_core with context %}

{% macro playbutton(modifier, duration) %}
    <div class="video-text-playbutton video-text-playbutton--{{ modifier }}">
        <span class="video-text-playbutton__text video-text-playbutton__text--{{ modifier }}">Video ansehen</span><span class="video-text-playbutton__duration">{{ duration | hide_none }}</span>
    </div>
{% endmacro %}
