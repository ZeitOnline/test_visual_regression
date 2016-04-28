{%- extends "zeit.web.campus:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-graphical{% endblock %}

{% block teaser_content %}
    <a class="{{ self.layout() }}__link" href="{{ teaser | create_url | append_campaign_params }}" title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}">
        {%- set module_layout = self.layout() -%}
        {%- include "zeit.web.campus:templates/inc/teaser/asset/image_zco-graphical.tpl" %}

        <h2 class="{{ self.layout() }}__heading">
            <span class="{{ self.layout() }}__tape"><span class="{{ self.layout() }}__kicker">
                {{- teaser.teaserSupertitle or teaser.supertitle -}}
            </span></span>
        </h2>
    </a>
{% endblock teaser_content %}
