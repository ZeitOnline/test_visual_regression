{#
Default teaser template to inherit from.
#}

{%- import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}
{%- import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{%- set image = get_image(module, fallback=True) %}
{%- set video = get_video(teaser) %}

<article class="{% block layout %}teaser{% endblock %} {% block layout_shade %}{% endblock %} {{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}"
         data-unique-id="{{ teaser.uniqueId }}"
         data-clicktracking="{{ area.kind }}"
         {%- block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}>

    {% if video -%}
        {# call video asset #}
            {% set href = teaser | create_url %}
            {{ cp.headervideo_linked(video, self.layout() + '__media-container ' + self.layout() + '__media-container--' + self.layout_shade(), '', href) }}
    {%- elif image -%}
        {# call image asset #}
        {% block teaser_image scoped %}
            {% set module_layout = self.layout() %}
            {% include "zeit.web.magazin:templates/inc/asset/image_teaser.tpl" %}
        {% endblock %}
    {%- endif %}

    {% block comments %}
        {% set comments = view.comment_counts[teaser.uniqueId] %}
        {% if comments and teaser.commentSectionEnable -%}
        <a href="{{ teaser | create_url }}#comments" class="cp_comment__counter">
            {{- lama.use_svg_icon('comments-count', 'cp_comment__icon', view.package) -}}
            <span class="cp_comment__count">{{ comments }}</span>
        </a>
        {%- endif %}
    {% endblock %}

    <a href="{{ teaser | create_url }}" class="{{ self.layout() }}__text" title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}">
        {% block icon %}{% endblock %}
        <h2>
            {% block teaser_kicker -%}
                <span class="{{ self.layout() }}__kicker">
                    {{- teaser.teaserSupertitle or teaser.supertitle -}}
                </span>
                {%- if teaser.teaserSupertitle or teaser.supertitle %}<span class="visually-hidden">: </span>{% endif %}
            {%- endblock %}

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
