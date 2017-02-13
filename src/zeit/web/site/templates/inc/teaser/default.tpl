{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% block teaser %}
<article class="
    {%- block layout %}{{ layout | default('default') }}{% endblock %} {% block teaser_modifier %}{% endblock %}
    {%- if module.visible_mobile == False %} mobile-hidden{% endif %}" data-unique-id="
    {{- teaser.uniqueId }}"
    {%- block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
    {%- block zplus_data %}{% if teaser is zplus_content %} data-zplus="zplus{% if teaser is zplus_registration_content %}-register{% endif %}"{% endif %}{% endblock %}
    {%- block taglogo_data %}{% if teaser | tag_with_logo_content %} data-taglogo="true"{% endif %}{% endblock %}
    {%- block teaser_attributes %}{% endblock %}>

    {% block teaser_label %}{% endblock %}
    {% block teaser_media_position_before_title %}{% endblock %}

    <div class="{{ self.layout() }}__container">

        {% block teaser_journalistic_format %}
            {% if teaser.serie and not teaser.serie.column %}
                <div class="{{ self.layout() }}__series-label">Serie: {{ teaser.serie.serienname }}</div>
            {% elif teaser.blog %}
                <div class="blog-format">
                    <span class="blog-format__marker">Blog</span>
                    <span class="blog-format__name">{{ teaser.blog.name }}</span>
                </div>
            {% endif %}
        {% endblock teaser_journalistic_format %}

        {% block teaser_heading %}
            <h2 class="{{ self.layout() }}__heading {% block teaser_heading_modifier %}{% endblock %}">
                {% block teaser_link %}
                <a class="{{ self.layout() }}__combined-link"
                   title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}"
                   href="{{ teaser | create_url | append_campaign_params }}">
                    {% block teaser_kicker %}
                        <span class="{{ '%s__kicker' | format(self.layout()) | with_mods(journalistic_format, area.kind, 'zmo' if teaser is zmo_content, 'zett' if teaser is zett_content, 'zco' if teaser is zco_content) }}">
                            {% block kicker_logo scoped %}
                                {% block content_kicker_logo %}
                                    {% set logo_layout = self.layout() %}
                                    {% for template in teaser | logo_icon(area.kind) %}
                                        {% include "zeit.web.core:templates/inc/badges/{}.tpl".format(template) %}
                                    {% endfor %}
                                {% endblock content_kicker_logo %}
                            {% endblock kicker_logo %}
                            {{ teaser.teaserSupertitle or teaser.supertitle -}}
                        </span>
                        {%- if teaser.teaserSupertitle or teaser.supertitle -%}
                            <span class="visually-hidden">:</span>
                        {% endif %}
                    {% endblock %}
                    {% block teaser_title %}
                    <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
                    {% endblock %}
                    {% block teaser_product %}
                       {# Use this for short teaser #}
                    {% endblock %}
                </a>
                {% endblock teaser_link %}
            </h2>
        {% endblock teaser_heading %}

        {% block teaser_media_position_after_title %}{% endblock %}

        {% block teaser_container %}
            {% block teaser_text %}
                {# TODO: Extract teaser-length text snippet from articles that don't have a teaser text. #}
                <p class="{{ self.layout() }}__text">{{ teaser.teaserText }}</p>
            {% endblock teaser_text %}
            {% block teaser_metadata_default %}
            <div class="{{ self.layout() }}__metadata">
                {% block teaser_byline %}
                    {% set byline = teaser | get_byline %}
                    {% if byline | length %}
                    <span class="{{ self.layout() }}__byline">
                        {%- include 'zeit.web.core:templates/inc/meta/byline.html' -%}
                    </span>
                    {% endif %}
                {% endblock teaser_byline %}
                {% block teaser_datetime %}
                    {% if not view.is_advertorial %}
                        {{ cp.include_teaser_datetime(teaser, self.layout(), area.kind) }}
                    {% endif %}
                {% endblock teaser_datetime %}
                {% block teaser_commentcount %}
                    {% set comments = view.comment_counts[teaser.uniqueId] %}
                    {% if comments and teaser.commentSectionEnable %}
                        {% set comments_string = comments | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') %}
                        <a class="{{ self.layout() }}__commentcount js-update-commentcount" href="{{ teaser | create_url }}#comments" data-ct-label="comments" title="Kommentare anzeigen">{{ comments_string }}</a>
                    {% endif %}
                {% endblock teaser_commentcount %}
            </div>
            {% endblock teaser_metadata_default %}
        {% endblock %}
    </div>

    {% block teaser_media_position_after_container %}{% endblock %}

</article>
{% endblock %}
