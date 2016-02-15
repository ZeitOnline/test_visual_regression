{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}

{% set image = teaser.image_group | closest_substitute_image('zon-column') %}
{# return zeit.web.core.template.get_image(content=self.context, variant_id='original', fallback=False) #}
{% set media_caption_additional_class = 'figcaption--hidden' %}
