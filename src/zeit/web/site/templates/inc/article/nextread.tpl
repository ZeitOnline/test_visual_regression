{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{%- set module = view.nextread -%}
{% if module is iterable -%}
<section class="nextread" id="nextread">
    {% for teaser in module %}
    {% set image = get_teaser_image(module, teaser) %}
    <a title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | translate_url }}">
        <div>{{ module.lead }}</div>
        {% include "zeit.web.site:templates/inc/teaser_asset/"+
            teaser | auto_select_asset | block_type +
            "_zon-fullwidth.tpl" ignore missing with context %}
        <div>{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</div>
        <div>{{ teaser.teaserTitle or teaser.title | hide_none }}</div>
        <div class="nextread__metadata">{{ cp.include_teaser_datetime(teaser, 'nextread') }}</div>
    </a>
    {% endfor %}
</section>
{% endif %}