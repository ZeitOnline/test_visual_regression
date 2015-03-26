{% import 'zeit.web.site:templates/macros/centerpage_macro_refactoring.tpl' as cp %}

{% set href = "/kultur/2012-03/fs-momente" %}
{% set image = teaser %}

<div class="cp-area cp-area--snapshot" id="snapshot" hidden>
    <div class="snapshot__title">Momentaufnahme</div>
    <a href="{{ href }}" class="snapshot-readmore"><span class="snapshot-readmore__item">Gesammelte Momente</span></a>
    {% include "zeit.web.site:templates/inc/teaser_asset/snapshot-image.tpl" ignore missing with context %}
    <div class="snapshot-caption">
        {{ teaser.attr_title | trim | hide_none }} {{ cp.image_copyright(teaser.copyright, 'snapshot-caption') }}</span>
    </div>
</div>
