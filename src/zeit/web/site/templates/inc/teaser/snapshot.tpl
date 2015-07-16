{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% set href = "/kultur/2012-03/fs-momente" %}
{% set image = teaser %}
{% set module_layout = 'snapshot' %}
{% set tracking_slug = 'snapshot..1.snapshot.'%}

<div class="snapshot" id="snapshot" hidden>
    <div class="snapshot__title">Momentaufnahme</div>
    <a href="{{ href }}" class="snapshot-readmore"{% if tracking_slug %} data-id="{{ tracking_slug }}text"{% endif %}><span class="snapshot-readmore__item">Gesammelte Momente</span></a>
    {% include "zeit.web.site:templates/inc/linked-image.tpl" %}
    <div class="snapshot-caption">
        {{ teaser.attr_title | trim | hide_none }} {{ cp.image_copyright(teaser.copyright, 'snapshot-caption') }}</span>
    </div>
</div>
