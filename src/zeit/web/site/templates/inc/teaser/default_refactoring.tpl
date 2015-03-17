{% import 'zeit.web.site:templates/macros/centerpage_macro_refactoring.tpl' as cp %}

{% block teaser %}

{% block teaser_media_position_before_teaser %}{% endblock %}

<article class="{% block layout %}{{ layout }}{% endblock %} {% block teaser_modifier %}{% endblock %}"{% if teaser_block %} data-block-type="{{ teaser_block.type | hide_none }}"{% endif %} data-unique-id="{{ teaser.uniqueId }}">

    {% block teaser_media_position_before_title %}{% endblock %}

    <div class="{{ self.layout() }}__container {% block teaser_container_modifier %}{% endblock %}">
        {% block teasaer_format_marker %}
        {% endblock %}
        {% block teasaer_format_name %}
        {% endblock %}
        <h2 class="{{ self.layout() }}__heading {% block teaser_heading_modifier %}{% endblock %}">
            {% block teaser_link %}
            <a class="{{ self.layout() }}__combined-link" title="{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }} - {{ teaser.teaserTitle or teaser.title | hide_none }}" href="{{ teaser.uniqueId | translate_url }}">
                {% block teaser_kicker %}
                <span class="{{ self.layout() }}__kicker">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</span>
                {% endblock %}
                {% block teaser_title %}
                <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title | hide_none }}</span>
                {% endblock %}
            </a>
            {% endblock %}

            {% block teaser_metadata_head %}{% endblock %}
        </h2>

        {% block teaser_media_position_after_title %}{% endblock %}

        {% block teaser_container %}
            {% block teaser_text %}
            <p class="{{ self.layout() }}__text">{{ teaser.teaserText }}{% block teaser_byline_inner %}{% endblock %}</p>
            {% endblock %}
            {% block teaser_byline %}
                {{ cp.include_teaser_byline(teaser, self.layout()) }}
            {% endblock %}
            {% block teaser_metadata_default %}
            <div class="{{ self.layout() }}__metadata">
                {% block teaser_datetime %}
                    {{ cp.include_teaser_datetime(teaser, self.layout()) }}
                {% endblock %}
                {% block teaser_commentcount%}
                    {{ cp.include_teaser_commentcount(teaser, self.layout()) }}
                {% endblock %}
            </div>
            {% endblock %}
        {% endblock %}
    </div>
    {% block teaser_media_position_after_container %}{% endblock %}

</article>
{% endblock %}
