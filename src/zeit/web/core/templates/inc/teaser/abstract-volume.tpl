<article class="volume-navigation {% block volumeteaser_modifier %}{% endblock %}" data-ct-area="{% block volumeteaser_ct_area %}{% endblock %}" data-ct-row="{% block volumeteaser_ct_row %}{% endblock %}" data-ct-column="false">

    <a class="volume-navigation__current" href="{% block volumeteaser_link %}{% endblock %}" title="{{ linklabel }}" data-ct-label="{{ linklabel }}">
        <span class="volume-navigation__packshot">
            {% set packshot = volume.covers['printcover'] %}
            {% set packshot_layout = 'volume-navigation' %}
            {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl" %}
        </span>
        <span class="volume-navigation__cta">
            <span class="volume-navigation__link">
            {{ linklabel }}
            </span>
        </span>
    </a>

    {% block volumeteaser_navigation %}{% endblock %}

</article>
