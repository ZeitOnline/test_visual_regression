{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% block teaser %}
{% profile %}

{% block teaser_media_position_before_teaser %}{% endblock %}

<article class="teaser {% block teaser_modifier %}{% endblock %}" data-unique-id="{{ teaser.uniqueId }}">
    {% block teaser_media_position_before_title %}{% endblock %}

    <h2 class="teaser__heading {% block teaser_heading_modifier %}{% endblock %}">
        {% block teaser_link %}
        <a class="teaser__combined-link" title="{{ teaser.teaserSupertitle }} - {{ teaser.teaserTitle }}" href="{{ teaser.uniqueId | translate_url }}">
            {% block teaser_kicker %}
            <span class="teaser__kicker">{{ teaser.teaserSupertitle }}</span>
            {% endblock %}
            {% block teaser_title %}
            <span class="teaser__title">{{ teaser.teaserTitle }}</span>
            {% endblock %}
        </a>
        {% endblock %}

        {% block teaser_metadata_head %}{% endblock %}
    </h2>

    {% block teaser_media_position_after_title %}{% endblock %}

    {% block teaser_container %}
    <div class="teaser__container {% block teaser_container_modifier %}{% endblock %}">
        {% block teaser_text %}
        <p class="teaser__text">{{ teaser.teaserText }}{% block teaser_byline_inner %}{% endblock %}</p>
        {% endblock %}
        {% block teaser_byline %}
            {{ cp.include_teaser_byline(teaser) }}
        {% endblock %}
        {% block teaser_metadata_default %}
        <div class="teaser__metadata">
            {% block teaser_datetime %}
                {{ cp.include_teaser_datetime(teaser) }}
            {% endblock %}
            {% block teaser_commentcount%}
                {{ cp.include_teaser_commentcount(teaser) }}
            {% endblock %}
        </div>
        {% endblock %}
    </div>
    {% endblock %}

</article>
{% endprofile %}
{% endblock %}
