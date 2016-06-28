{% extends 'zeit.web.core:templates/macros/layout_macro.tpl' %}

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
