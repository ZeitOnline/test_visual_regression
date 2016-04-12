{#
Default teaser template to inherit from.
#}

{%- import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}
{%- import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{%- set image = get_image(module, teaser, fallback=True) %}
{%- set video = teaser | get_video_asset %}
{%- set area = area if area else '' %} {# TODO: remove as soon as we have access to real area data (AS)#}

<article class="{% block layout %}teaser{% endblock %} {% block layout_shade %}{% endblock %} {{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}"
         data-unique-id="{{ teaser.uniqueId }}"
         data-clicktracking="{{ area.kind }}"
         {%- block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}>

    {% block comments %}
        {% if view.comment_counts[teaser.uniqueId] -%}
        <a href="{{ teaser | create_url }}#show_comments" class="cp_comment__counter">
            {{- lama.use_svg_icon('comments-count', 'cp_comment__icon', request) -}}
            <span class="cp_comment__count">{{ view.comment_counts[teaser.uniqueId] }}</span>
        </a>
        {%- endif %}
    {% endblock %}

    {% if video -%}
        {# call video asset #}
            {% set href = teaser | create_url %}
            {{ cp.headervideo_linked(video, self.layout() + '__media-container ' + self.layout() + '__media-container--' + self.layout_shade(), '', href) }}
    {%- elif image -%}
        {# call image asset #}
        {% block teaser_image scoped %}
            {% set media_caption_additional_class = 'figcaption--hidden' %}
            {% set module_layout = self.layout() %}
            {% set href = teaser | create_url %}
            {% include "zeit.web.core:templates/inc/asset/image_linked.tpl" %}
        {% endblock %}
    {%- endif %}


    <a href="{{ teaser | create_url }}" class="{{ self.layout() }}__text">
        {% block icon %}{% endblock %}
        <h2>
            {% block teaser_kicker %}
            <span class="{{ self.layout() }}__kicker">
                {{- teaser.teaserSupertitle or teaser.supertitle -}}
            </span>
            {% endblock %}
            <span class="{{ self.layout() }}__title">
                {{- teaser.teaserTitle or teaser.title -}}
            </span>
        </h2>
        {% block teaser_text %}
        <p class="{{ self.layout() }}__subtitle">
            {{- teaser.teaserText -}}
        </p>
        {% endblock %}
    </a>

</article>
