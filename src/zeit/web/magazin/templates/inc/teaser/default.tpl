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
#}

{%- import 'zeit.web.magazin:templates/macros/centerpage_macro.tpl' as cp with context %}
{%- import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}
{%- import 'zeit.web.magazin:templates/macros/article_macro.tpl' as blocks with context %}

{% set image = get_teaser_image(module, teaser) %}
{%- set video = teaser | get_video_asset %}
{% set area = area if area else '' %} {# TODO: remove as soon as we have access to real area data (AS)#}

<article class="{% block layout %}teaser{% endblock %} {{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}"
         data-unique-id="{{ teaser.uniqueId }}"
         {% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
         data-clicktracking="{{ area.kind }}"
         {% block teaser_attributes %}{% endblock %}>

    {% block comments %}
        {% if view.comment_counts[teaser.uniqueId] %}
        <a href="{{ teaser | create_url }}#show_comments">
            <span class="cp_comment__count__wrap icon-comments-count">{{ view.comment_counts[teaser.uniqueId] }}</span>
        </a>
        {% endif %}
    {% endblock %}

    <a href="{{ teaser | create_url }}">

        {% if video -%}
            {# call video asset #}
            {{ blocks.headervideo(video, 'cp_leader__asset cp_leader__asset--' + self.layout_shade(), '') }}
        {%- elif image -%}
            {# call image asset #}
            <div class="scaled-image is-pixelperfect {{ self.layout() }}__image {{ self.layout() }}__asset {{ self.layout() }}--{% block layout_shade %}dark{% endblock %}">
                {{ lama.insert_responsive_image(image) }}
            </div>
        {%- endif %}

        <header class="{{ self.layout() }}__title__wrap {{ self.layout() }}__title__wrap--{{ self.layout_shade() }}">
            {% block icon %}{% endblock %}
            <h2>
                {% block teaser_kicker %}
                <div class="{{ self.layout() }}__supertitle">
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
