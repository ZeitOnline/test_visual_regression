{#

Default teaser template to inherit from.

Available attributes:
    cp
    lama
    module
    teaser

All calling templates have to provide:
    subtitle: to define display of subtitle ('true'/ 'false')
    format: to define type of button (eg. 'small'/ 'large'/ 'large-photo'/ 'gallery'/ 'mtb'/ 'default')
    supertitle: to define display of supertitle ('true'/ 'false')
    icon: define display of optional asset icon ('true'/ 'false')
    image_class: define optional class for images (eg. extra behaviour mtb)
#}

{% import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}
{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{%- set image = get_teaser_image(module, teaser) %}

<div class="cp_button cp_button--{{ self.format() }}{{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}">

    {{ cp.comment_count(view.comment_counts[teaser.uniqueId], teaser | create_url) }}
    <a href="{{ teaser | create_url }}">

        {% if self.image_class() != 'false' -%}
            {# call image asset with optional class #}
            <div class="scaled-image">
                {{ lama.insert_responsive_image(image, self.image_class()) }}
        {%- else -%}
            {# call standard image asset #}
            <div class="scaled-image is-pixelperfect cp_button__image">
                {{ lama.insert_responsive_image(image) }}
        {%- endif %}
            </div>
    </a>

    {# call teaser text #}
    {{ cp.teaser_text_block(teaser, 'button', 'none', self.supertitle(), self.subtitle(), self.icon()) }}
</div>
