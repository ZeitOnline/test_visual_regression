{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% set href = module.read_more_url %}
{% set image = get_gallery_image(module, teaser) %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
{% set tracking_slug = '{}...{}.'.format(region_loop.index, layout) %}
{% set module_layout = 'snapshot' %}

<div class="{{ module_layout }}">
    {{ cp.section_heading(module.title, module.read_more, module.read_more_url, None, tracking_slug + 'gesammelte_momente') }}
    {% include "zeit.web.core:templates/inc/asset/image_linked.tpl" %}
    <div class="snapshot-caption">
        {{ image.caption | trim }} {{ cp.image_copyright(image.copyright, 'snapshot-caption') }}
    </div>
</div>
