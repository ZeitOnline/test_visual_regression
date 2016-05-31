{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% set tracking_slug = '{}...{}.'.format(region_loop.index, layout) %}
{% set module_layout = 'snapshot' %}

<div class="{{ module_layout }}">
    {{ cp.section_heading(module.title, module.read_more, module.read_more_url, None, tracking_slug + 'gesammelte_momente') }}
    {% include "zeit.web.site:templates/inc/asset/image_snapshot.tpl" %}
</div>
