{#
Default teaser template to inherit from.
#}
{%- import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}
{%- import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama with context %}

{%- set image = get_image(module, fallback=True) %}
{%- set video = get_video(teaser) %}

<article class="{% block layout %}teaser{% endblock %} {% block layout_shade %}{% endblock %} {{ cp.advertorial_modifier(teaser.product, view.is_advertorial) | default('') }}"
         data-unique-id="{{ teaser.uniqueId }}"
         {%- block zplus_data %}{% if teaser is zplus_content %} data-zplus="zplus{% if teaser is zplus_registration_content %}-register{% endif %}"{% endif %}{% endblock %}
         {%- block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}>

    {% if video -%}
        {# call video asset #}
        {% block teaser_video %}
            {% set href = teaser | create_url %}
            {{ cp.headervideo_linked(video, self.layout() + '__media-container ' + self.layout() + '__media-container--' + self.layout_shade(), '', href) }}
        {% endblock %}
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
        <a href="{{ teaser | create_url }}#comments" class="cp_comment__counter" data-ct-label="comments">
            {{- lama.use_svg_icon('comments-count', 'cp_comment__icon', view.package) -}}
            <span class="cp_comment__count">{{ comments }}</span>
        </a>
        {%- endif %}
    {% endblock %}

    <div class="{{ self.layout() }}__text">

        {% block icon %}{% endblock %}

        {% block teaser_journalistic_format -%}
            {% if view.context is seriespage  -%}
            {% elif teaser.serie and not teaser.serie.column and not teaser.serie.serienname == 'Martenstein' -%}
                <div class="{{ '%s__series-label' | format(self.layout()) }}">Serie: {{ teaser.serie.serienname }}</div>
            {% endif -%}
        {% endblock teaser_journalistic_format -%}

        <a href="{{ teaser | create_url }}" class="{{ self.layout() }}__link" title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}">
            <h2 class="{{ self.layout() }}__title-box">
                {% block teaser_kicker -%}
                    {% block zplus_kicker_logo %}
                        {% if teaser is zplus_abo_content %}
                            {{ lama.use_svg_icon('zplus', 'zplus-logo zplus-logo--xs', view.package, a11y=False) }}
                        {% elif teaser is zplus_registration_content and toggles('zplus_badge_gray') %}
                            {{ lama.use_svg_icon('zplus', 'zplus-logo-register zplus-logo--xs', view.package, a11y=False) }}
                        {% endif %}
                    {% endblock %}
                    <span class="{{ self.layout() }}__kicker">
                        {{- teaser.teaserSupertitle or teaser.supertitle -}}
                    </span>
                    {%- if teaser.teaserSupertitle or teaser.supertitle %}<span class="visually-hidden">: </span>{% endif %}
                {%- endblock %}

                {% block teaser_title -%}
                <span class="{{ self.layout() }}__title">
                    {{- teaser.teaserTitle or teaser.title -}}
                </span>
                {%- endblock teaser_title %}
            </h2>
            {% block teaser_text %}
            <p class="{{ self.layout() }}__subtitle">
                {{- teaser.teaserText -}}
            </p>
            {% endblock %}
        </a>

    </div>

</article>
