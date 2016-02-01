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

{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{%- set image = get_teaser_image(module, teaser) %}

<div class="cp_button cp_button--{{ self.format() }}{{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}">

    {% if view.comment_counts[teaser.uniqueId] %}
        <a href="{{ teaser | create_url }}#show_comments">
            <span class="cp_comment__count__wrap icon-comments-count">{{ view.comment_counts[teaser.uniqueId] }}</span>
        </a>
    {% endif %}

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

    <header class="cp_button__title__wrap cp_button__title__wrap{% block shade %}{% endblock %}">
        <a href="{{teaser | create_url}}">
            {% block icon %}{% endblock %}
            <h2>
                {% if supertitle != 'false' %}
                    <div class="cp_button__supertitle">
                        {% if teaser.teaserSupertitle %}
                            {{ teaser.teaserSupertitle }}
                        {% elif teaser.supertitle %}
                            {{ teaser.supertitle }}
                        {% endif %}
                    </div>
                {% endif %}
                <div class="cp_button__title">
                    {{ teaser.teaserTitle }}
                </div>
            </h2>
            {% block teaser_text %}
                <span class="cp_button__subtitle">
                    {{ teaser.teaserText }}
                </span>
            {% endblock %}
        </a>
    </header>
</div>
