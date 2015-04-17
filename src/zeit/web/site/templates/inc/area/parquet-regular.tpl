<div class="cp-area cp-area--parquet">
    <div class="parquet-row">
        <div class="parquet-meta">
            {% if area.referenced_cp is none %}
                <span class="parquet-meta__title">
                    {{ area.title | hide_none }}
                </span>
            {% else %}
                <a class="parquet-meta__title" href="{{ area.referenced_cp.uniqueId | translate_url }}">
                    {{ area.title | hide_none }}
                </a>
                <ul class="parquet-meta__topic-links">
                    {% for label, link in topiclinks(area.referenced_cp) %}
                        <li>
                            <a href="{{ link }}" class="parquet-meta__topic-link">
                                {{ label }}
                            </a>
                        </li>
                    {% endfor %}
                </ul>
            {% endif %}

            {% if area.read_more and area.read_more_url %}
                <a href="{{ area.read_more_url }}" class="parquet-meta__more-link">
                    {{ area.read_more }}
                </a>
            {% endif %}
        </div>
        <ul class="parquet-teasers">
            {% for module in area.values() -%}
                {% set teaser = module | first_child %}
                {% if loop.index <= area.display_amount %}
                    {% include ["zeit.web.site:templates/inc/teaser/" + module | get_layout + "_position_" + loop.index | string + ".tpl",
                                "zeit.web.site:templates/inc/teaser/zon-parquet-small.tpl"] %}
                {% endif %}
            {% endfor %}
        </ul>
    </div>
</div>
