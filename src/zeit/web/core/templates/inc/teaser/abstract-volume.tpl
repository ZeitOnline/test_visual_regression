<article class="teaser-volume {% block volumeteaser_modifier %}{% endblock %}" data-ct-area="{% block volumeteaser_ct_area %}{% endblock %}" data-ct-row="{% block volumeteaser_ct_row %}{% endblock %}" data-ct-column="false">

    <a class="teaser-volume__current" href="{% block volumeteaser_link %}{% endblock %}" title="{{ linklabel }}" data-ct-label="{{ linklabel }}">
        <span class="teaser-volume__packshot">
            {% set packshot = volume.covers['printcover'] %}
            {% set packshot_layout = 'teaser-volume' %}
            {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl" %}
        </span>
        <span class="teaser-volume__cta">
            <span class="teaser-volume__link">
            {{ linklabel }}
            </span>
        </span>
    </a>

    {% block volumeteaser_navigation %}{% endblock %}

</article>
