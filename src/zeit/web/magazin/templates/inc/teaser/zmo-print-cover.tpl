{#
Teaser template for Zeit Magazin print cover
#}

{% import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}
{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{%- set image = get_teaser_image(module, teaser) -%}

<div class="teaser-print-cover teaser-print-cover">
    <a href="{{ teaser | create_url }}">
        <div class="scaled-image teaser-print-cover__image">
            {{ lama.insert_responsive_image(image) }}
        </div>
    </a>
    {{ cp.teaser_text_block(teaser, 'button', 'none', 'true', 'false') }}
</div>
