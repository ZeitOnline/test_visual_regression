{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% set module = view.nextread %}
{% set teaser = module | first_child %}
{% set image = get_teaser_image(module, teaser) %}
{% set has_default_image = get_default_image_id() in image.uniqueId %}

{% macro nextread_build_class(element) -%}
    nextread__{{ element }}{% if not has_default_image %} nextread__{{ element }}--with-image{% endif %}
{%- endmacro %}

<div class="nextread{% if not has_default_image %} nextread--with-image{% endif %}" id="nextread">
    <a class="{{ nextread_build_class('link') }}" title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}">
        <div class="{{ nextread_build_class('lead') }}">{{ module.lead or 'Lesen Sie jetzt' }}</div>
        {% if image and not has_default_image -%}
            {% set module_layout = 'nextread' %}
            {% include "zeit.web.site:templates/inc/teaser_asset/{}_zon-nextread.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
        {%- endif -%}
        <div class="{{ nextread_build_class('helper') }}">
            <div class="{{ nextread_build_class('inner-helper') }}">
                <div class="{{ nextread_build_class('kicker') }}">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</div>
                <div class="{{ nextread_build_class('title') }}">{{ teaser.teaserTitle or teaser.title | hide_none }}</div>
                <div class="{{ nextread_build_class('metadata') }}">{{ cp.include_teaser_datetime(teaser, 'nextread') }}</div>
            </div>
        </div>
    </a>
</div>
