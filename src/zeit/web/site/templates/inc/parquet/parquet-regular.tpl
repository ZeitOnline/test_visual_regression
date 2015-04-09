{% set row = area.values()[0] %}

{% profile %}
<div class="cp-area cp-area--parquet" id="parquet">
    <div class="parquet-row">
        <div class="parquet-meta">
            {% if row.referenced_cp is none %}{# parquet data model is a mess #}
                <span class="parquet-meta__title">
                    {{ row.title }}
                </span>
            {% else %}{# for genuine centerpages #}
                <a class="parquet-meta__title" href="{{ row.referenced_cp.uniqueId | translate_url }}">
                    {{ row.title }}
                </a>
                <ul class="parquet-meta__topic-links">
                    {% for label, link in topiclinks(row.referenced_cp) %}
                        <li>
                            <a href="{{ link }}" class="parquet-meta__topic-link">
                                {{ label }}
                            </a>
                        </li>
                    {% endfor %}
                </ul>
            {% endif %}

            {% if row.read_more and row.read_more_url %}
                <a href="{{ row.read_more_url }}" class="parquet-meta__more-link">
                    {{ row.read_more }}
                </a>
            {% endif %}
        </div>
        <ul class="parquet-teasers">
            {% for teaser in row -%}
                {% if loop.index <= row.display_amount %}
                    {% include ["zeit.web.site:templates/inc/parquet/" + row | get_teaser_layout(loop.index - 1) + "_position_" + loop.index | string + ".tpl",
                                "zeit.web.site:templates/inc/parquet/" + row | get_teaser_layout(loop.index - 1) + ".tpl" + "highly-sophisticated-feature-toggle_off",
                                "zeit.web.site:templates/inc/parquet/zon-parquet-small.tpl"] %}
                {% endif %}
            {% endfor %}
        </ul>
    </div>
</div>
{% endprofile %}
