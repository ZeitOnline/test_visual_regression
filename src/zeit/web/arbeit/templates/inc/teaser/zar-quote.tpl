{%- extends "zeit.web.arbeit:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-quote{% endblock %}

{# The quote teaser has another order of content (text, heading, image) #}

{% block teaser_allcontent %}
    {% block teaser_text %}
        <a class="{{ self.layout() }}__quotelink"
                   title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}"
                   href="{{ teaser | create_url | append_campaign_params }}">
            {{- super() }}</a>{% endblock %}

    <div class="{{ self.layout() }}__headingwrapper">
        {% block teaser_heading %}{{ super() }}{% endblock %}
        {% block teaser_byline %}{{ super() }} {{ lama.use_svg_icon('arrow-right', 'teaser-quote__byline-arrow', view.package, a11y=False) }}{% endblock %}
    </div>

    {% block teaser_media %}
        {% set module_layout = self.layout() %}
        {% include "zeit.web.arbeit:templates/inc/teaser/asset/image_teaser_zar-quote.tpl" %}
    {% endblock %}
{% endblock %}
