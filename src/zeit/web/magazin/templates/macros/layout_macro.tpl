{% extends 'zeit.web.core:templates/macros/layout_macro.tpl' %}

{% macro insert_responsive_image(image, image_class, page_type) %}
    {# TRASHME: I want to be replace by the new snazzy image.tpl #}
    {% if image %}
        {% set source = image | default_image_url %}
        <!--[if gt IE 8]><!-->
            <noscript data-src="{{ source }}">
        <!--<![endif]-->
        {% if page_type == 'article' and image.href %}
            <a href="{{ image.href }}">
        {% endif %}
                <img alt="{{ image.alt }}"{% if image.title %} title="{{ image.title }}"{% endif %} class="{{ image_class | default('', true) }} figure__media" src="{{ source }}" data-src="{{ source }}" data-ratio="{{ image.ratio }}"{% if image.itemprop %} itemprop="{{ image.itemprop }}"{% endif %}>
        {% if page_type == 'article' and image.href %}
            </a>
        {% endif %}
        <!--[if gt IE 8]><!-->
            </noscript>
        <!--<![endif]-->
    {% endif %}
{% endmacro %}

{% macro copyrights(cr_list) -%}
    <div id="copyrights" class="copyrights">
        {{ use_svg_icon('copyrights-close', 'js-toggle-copyrights copyrights__close copyrights__close--icon', view.package) }}
        <section class="copyrights__wrapper is-centered is-constrained">
            <span class="copyrights__title">Bildrechte auf dieser Seite</span>
            <ul class="copyrights__list">
                {%- for cr in cr_list -%}
                <li class="copyrights__entry">
                    <div class="copyrights__image" style="background-image: url({{ cr.image }});"></div>
                    <span class="copyrights__label">
                        {%- if cr.link -%}
                            <a href="{{ cr.link }}"{% if cr.nofollow %} rel="nofollow"{% endif %}>{{ cr.label }}</a>
                        {%- else -%}
                            {{ cr.label }}
                        {%- endif -%}
                    </span>
                </li>
                {%- endfor -%}
            </ul>
        </section>
        <a class="js-toggle-copyrights copyrights__close copyrights__close--label">Bereich schließen</a>
        <div style="clear:both"></div>
    </div>
{%- endmacro %}
