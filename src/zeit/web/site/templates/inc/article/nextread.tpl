{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% set module = view.nextread %}
{% set teaser = module | first_child %}
{% set image = get_teaser_image(module, teaser) %}
{% set has_default_image = get_default_image_id() in image.uniqueId %}

<div class="nextread {% if has_default_image %}nextread--without-image{% endif %}" id="nextread">
    <a class="nextread__link {% if has_default_image %}nextread__link--without-image{% endif %}" title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}">
        <div class="nextread__lead{% if has_default_image %} nextread__lead--without-image{% endif %}">{{ module.lead or 'Lesen Sie jetzt' }}</div>
        {% if image %}
            {%- if not has_default_image -%}
                {% set module_layout = 'nextread' %}
                {% include "zeit.web.site:templates/inc/teaser_asset/{}_zon-nextread.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
            {%- endif -%}
        {%- endif -%}
        <div class="nextread__helper {% if has_default_image %}nextread__helper--without-image{% endif %}">
            <div class="nextread__inner-helper {% if has_default_image %}nextread__inner-helper--without-image{% endif %}">
                <div class="nextread__kicker">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</div>
                <div class="nextread__title">{{ teaser.teaserTitle or teaser.title | hide_none }}</div>
                <div class="nextread__metadata">{{ cp.include_teaser_datetime(teaser, 'nextread') }}</div>
            </div>
        </div>
    </a>
</div>
