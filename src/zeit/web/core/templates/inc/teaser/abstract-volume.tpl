{#
"teaser-volumeteaser": Naming things only to satisfy AuDev.
> "Die Packshots auf CPs sollen der Standardverpixelung folgen.
> Die Bezeichnung des Packshot sollte aber parallel zum Format
> für Packshots in Artikeln bleiben, also `volumeteaser`."
#}
<article class="{% block volumeteaser_blockname %}teaser-volumeteaser{% endblock %} {% block volumeteaser_modifier %}{% endblock %}" {% block volumeteaser_data_ct %}{% endblock %}>

    <a class="{{ self.volumeteaser_blockname() }}__current" href="{% block volumeteaser_link %}{% endblock %}" title="{{ linklabel }}" {% block volumeteaser_data_ct_label %}{% endblock %}>
        <span class="{{ self.volumeteaser_blockname() }}__packshot">
            {% set packshot = volume.covers['printcover'] %}
            {% set packshot_layout = self.volumeteaser_blockname() %}
            {% include "zeit.web.core:templates/inc/asset/image_packshot.tpl" %}
        </span>
        <span class="{{ self.volumeteaser_blockname() }}__cta">
            <span class="{{ self.volumeteaser_blockname() }}__link">
            {{ linklabel }}
            </span>
        </span>
    </a>

    {% block volumeteaser_navigation %}{% endblock %}

</article>
