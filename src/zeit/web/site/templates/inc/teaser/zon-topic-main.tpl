{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-topic-main{% endblock %}

{#% block teaser_modifier %}teaser--ispositioned teaser--islight{% endblock %#}
{#% block teaser_heading_modifier %}teaser__heading--issized{% endblock %#}
{#% block teaser_container_modifier %}teaser__container--issized-desktop{% endblock %#}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "_zop-topic.tpl" ignore missing with context %}
    <div class="{{ self.layout() }}__inner-helper">
        <a href="{{ teaser.uniqueId | translate_url }}">
            <span class="{{ self.layout() }}__introduction">Thema im Überblick</span>
        </a>
{% endblock %}

{% block teaser_kicker %}
{% endblock %}

{% block teaser_media_position_after_container %}
    </div>
    <ul class="{{ self.layout() }}__relateds">
    {% for related in list(block)[1:] %}
        <li class="{{ self.layout() }}__related">
            <a href="{{ related.uniqueId | translate_url }}">
                <span class="{{ self.layout() }}__related-kicker">{{ related.teaserSupertitle }}</span>
            </a>
            <a href="{{ related.uniqueId | translate_url }}">
                <span class="{{ self.layout() }}__related-title">{{ related.teaserTitle }}</span>
            </a>
        </li>
    {% endfor %}
    </ul>
{% endblock %}

{% block teaser_media_position_after_title %}
    <a href="{{ teaser.uniqueId | translate_url }}">
        <span class="{{ self.layout() }}__readmore">Alles zum Thema</span>
    </a>
{% endblock %}
