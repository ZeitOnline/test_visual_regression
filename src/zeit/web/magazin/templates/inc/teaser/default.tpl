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
{% import 'zeit.web.magazin:templates/macros/layout_macro.tpl' as lama with context %}

{% set image = get_teaser_image(module, teaser) %}
{% set area = area if area else '' %} {# TODO: remove as soon as we have access to real area data (AS)#}

<article class="cp_button cp_button--{% block format %}{% endblock %}
                {{ cp.advertorial_modifier(teaser.product_text, view.is_advertorial) | default('') }}"
         data-unique-id="{{ teaser.uniqueId }}"
         {% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
         data-clicktracking="{{ area.kind }}"
         {% block teaser_attributes %}{% endblock %}>

    {% if view.comment_counts[teaser.uniqueId] %}
    <a href="{{ teaser | create_url }}#show_comments">
        <span class="cp_comment__count__wrap icon-comments-count">{{ view.comment_counts[teaser.uniqueId] }}</span>
    </a>
    {% endif %}

    <a href="{{ teaser | create_url }}">

        <div class="scaled-image is-pixelperfect cp_button__image">
            {{ lama.insert_responsive_image(image) }}
        </div>

        <header class="cp_button__title__wrap cp_button__title__wrap{% block shade %}{% endblock %}">
            {% block icon %}{% endblock %}
            <h2>
                {% block teaser_kicker %}
                <div class="cp_button__supertitle">
                    {{ teaser.teaserSupertitle or teaser.supertitle }}
                </div>
                {% endblock %}
                <div class="cp_button__title">
                    {{ teaser.teaserTitle or teaser.title }}
                </div>
            </h2>
            {% block teaser_text %}
            <span class="cp_button__subtitle">
                {{ teaser.teaserText }}
            </span>
            {% endblock %}
        </header>
    </a>
</article>
