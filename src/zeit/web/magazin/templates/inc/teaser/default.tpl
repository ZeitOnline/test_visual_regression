{#
Default teaser template to inherit from.
#}

{%- import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}
{%- import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}
{%- import 'zeit.web.magazin:templates/macros/article_macro.tpl' as blocks with context %}

{%- set image = get_teaser_image(module, teaser) %}
{%- set video = teaser | get_video_asset %}
{%- set area = area if area else '' %} {# TODO: remove as soon as we have access to real area data (AS)#}

<article class="{% block layout %}teaser{% endblock %} {% block layout_shade %}{% endblock %} {{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}"
         data-unique-id="{{ teaser.uniqueId }}"
         {% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
         data-clicktracking="{{ area.kind }}"
         {% block teaser_attributes %}{% endblock %}>

    {% block comments %}
        {% if view.comment_counts[teaser.uniqueId] %}
        <a href="{{ teaser | create_url }}#show_comments">
            <span class="{{ self.layout() }}__comments icon-comments-count">{{ view.comment_counts[teaser.uniqueId] }}</span>
        </a>
        {% endif %}
    {% endblock %}

    <a href="{{ teaser | create_url }}">

        {% if video -%}
            {# call video asset #}
            {{ blocks.headervideo(video, self.layout() + '__asset ' + self.layout() + '__asset--' + self.layout_shade(), '') }}
        {%- elif image -%}
            {# call image asset #}
            {% block teaser_image %}
                {% set href = teaser | create_url | append_campaign_params %}
                {% set media_caption_additional_class = 'figcaption--hidden' %}
                {% set module_layout = self.layout() %}
                {% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" %}
            {% endblock %}
        {%- endif %}

        <header class="{{ self.layout() }}__text">
            {% block icon %}{% endblock %}
            <h2>
                {% block teaser_kicker %}
                <div class="{{ self.layout() }}__kicker">
                    {{ teaser.teaserSupertitle or teaser.supertitle }}
                </div>
                {% endblock %}
                <div class="{{ self.layout() }}__title">
                    {{ teaser.teaserTitle or teaser.title }}
                </div>
            </h2>
            {% block teaser_text %}
            <span class="{{ self.layout() }}__subtitle">
                {{ teaser.teaserText }}
            </span>
            {% endblock %}
        </header>
    </a>
</article>
