{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% set path = 'kultur/2012-03/fs-momente' %}
{% set href = '{}{}'.format(view.request.route_url('home'), path) %}
{% set image = teaser %}
{% set module_layout = 'snapshot' %}
{% set tracking_slug = '{}...{}.'.format(region_loop.index, module_layout) %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{# TODO: Why not extend the image-linked.tpl directly? #}
<div class="snapshot" id="snapshot" hidden>
    {{ cp.section_heading('Momentaufnahme', 'Gesammelte Momente', path, view, tracking_slug + 'gesammelte_momente') }}
    {% include "zeit.web.site:templates/inc/asset/image_linked.tpl" %}
    <div class="snapshot-caption">
        {{ teaser.title | trim }} {{ cp.image_copyright(teaser.copyright, 'snapshot-caption') }}</span>
    </div>
</div>
