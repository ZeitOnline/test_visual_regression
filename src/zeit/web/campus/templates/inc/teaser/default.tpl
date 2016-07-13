{% import 'zeit.web.campus:templates/macros/centerpage_macro.tpl' as cp %}

<article class="{% block layout %}{{ layout | default('default') }}{% endblock %} {% block teaser_modifier %}{% endblock %}{% if module.visible_mobile == False %} mobile-hidden{% endif %}"
    data-unique-id="{{ teaser.uniqueId }}"
    {% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
    data-clicktracking="{{ area.kind }}"
    {% block teaser_attributes %}{% endblock %} itemscope itemtype="http://schema.org/Article" itemref="publisher">

    {% block teaser_media %}{% endblock %}

    {% block teaser_content %}
        {% block teaser_heading %}
            <h2 class="{{ self.layout() }}__heading {% block teaser_heading_modifier %}{% endblock %}"
                {%- if not self.teaser_journalistic_format() | length %} itemprop="headline"{% endif %}>
                {% block teaser_link -%}
                <a class="{{ self.layout() }}__combined-link"
                   title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}"
                   href="{{ teaser | create_url | append_campaign_params }}" itemprop="mainEntityOfPage">
                    {% block teaser_kicker %}
                        {% if teaser.teaserSupertitle or teaser.supertitle %}
                            <span class="{{ '%s__kicker' | format(self.layout()) | with_mods('leserartikel' if teaser is leserartikel) }}">
                                {% block teaser_journalistic_format -%}
                                    {% if teaser.serie -%}
                                        <span class="series-label">{{ teaser.serie.serienname }}</span>
                                    {% elif teaser.blog -%}
                                        <span class="blog-label">{{ teaser.blog.name }}</span>
                                    {%- endif %}
                                {%- endblock teaser_journalistic_format %}

                                <span>{{ teaser.teaserSupertitle or teaser.supertitle }}</span>
                            </span>
                            <span class="visually-hidden">: </span>
                        {%- endif %}
                    {% endblock %}
                    {% block teaser_title %}
                        <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
                    {% endblock %}
                </a>
                {% endblock teaser_link %}
                {%- if self.teaser_journalistic_format() | length -%}
                    <meta itemprop="headline" content="{{ teaser.teaserSupertitle or teaser.supertitle }}: {{ teaser.teaserTitle or teaser.title }}">
                {%- endif -%}
            </h2>
        {% endblock teaser_heading %}

        {% block teaser_media_position_after_title %}{% endblock %}

        {% block teaser_container %}
            {% block teaser_text %}
                <p class="{{ self.layout() }}__text" itemprop="description">{{ teaser.teaserText }}</p>
            {% endblock teaser_text %}
            {% block teaser_metadata_default %}
            <div class="{{ self.layout() }}__metadata">
                {% block teaser_byline %}
                    {% set byline = teaser | get_byline('author') %}
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
                        <a class="{{ self.layout() }}__commentcount js-update-commentcount" href="{{ teaser | create_url }}#comments" title="Kommentare anzeigen">{{ comments_string }}</a>
                    {% endif %}
                {% endblock teaser_commentcount %}
            </div>
            {% endblock teaser_metadata_default %}
        {% endblock teaser_container %}

    {% endblock teaser_content %}
    <meta itemprop="datePublished" content="{{ teaser | release_date | format_date('iso8601') }}">
    <meta itemprop="dateModified" content="{{ teaser | mod_date | format_date('iso8601') }}">
</article>
