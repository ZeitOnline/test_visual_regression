{#

Default teaser template for nextread teasers

Available attributes:
    lama
    teaser
    module

All calling templates have to provide:
    teaser_image: to define display of teaser image ('true', 'false')
    bg_image: to define display of background image ('true', 'false')
#}

{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{% set image = get_teaser_image(module, teaser) %}
{% set bg_image = '' %}

{# if we have to display a bg image, prepare it here #}
{% if self.bg_image() == 'true' %}
    {% if image %}
        {% set bg_image = 'background-image: url(' + image | default_image_url | default('http://placehold.it/160x90', true) + ')' %}
    {% else %}
        {% set bg_image = 'background-color: #252525;' %}
    {% endif %}
{% endif %}

<div class="article__nextread__body article__nextread__body--{{ module.multitude }}{% if not image %} article__nextread__body--no-img{% endif %}" style="{{ bg_image }}">
    <a title="{{ teaser.supertitle }}: {{ teaser.title }}" href="{{ teaser.uniqueId | create_url }}">
        
        {# display bg image #}
        {% if image and self.teaser_image() == 'true' %}
            <div class="scaled-image article__nextread__img article__nextread__img--{{ module.multitude }}">
                {{ lama.insert_responsive_image(image) }}
            </div>
        {% endif %}

        {# display nextread text #}
        <div class="article__nextread__article article__nextread__article--{{ module.multitude }}">
            <span class="article__nextread__supertitle">{{ teaser.supertitle }}</span>
            <span class="article__nextread__title">{{ teaser.title }}</span>
        </div>
    </a>
</div>
