{% set row = view.spektrum_hp_feed %}

{% if row | length %}
{% profile %}
<div class="cp-area cp-area--parquet" id="parquet">
    <div class="parquet-row parquet-row--spektrum" id="parquet-spektrum">
        {%- if parquet_position -%}
            {% set track_slug = 'hp.centerpage.teaser.parquet.' + parquet_position %}
        {%- endif -%}
        <div class="parquet-meta">
            <a {% if track_slug %}id="{{ track_slug }}.1|http://www.spektrum.de"{% endif %} class="parquet-meta__title parquet-meta__title--spektrum" href="http://www.spektrum.de"><span class="parquet-meta__logo parquet-meta__logo--spektrum icon-logo-spektrum">Spektrum.de</span></a>
            <ul class="parquet-meta__topic-links parquet-meta__topic-links--spektrum">
                <li>
                    <a {% if track_slug %}id="{{ track_slug }}.1.a|http://www.spektrum.de/astronomie"{% endif %} href="http://www.spektrum.de/astronomie" class="parquet-meta__topic-link">Astronomie</a>
                </li>
                <li>
                    <a {% if track_slug %}id="{{ track_slug }}.1.b|http://www.spektrum.de/biologie"{% endif %} href="http://www.spektrum.de/biologie" class="parquet-meta__topic-link">Biologie</a>
                </li>
                <li>
                    <a {% if track_slug %}id="{{ track_slug }}.1.c|http://www.spektrum.de/psychologie-hirnforschung"{% endif %} href="http://www.spektrum.de/psychologie-hirnforschung" class="parquet-meta__topic-link">Psychologie</a>
                </li>
            </ul>
            <div class="parquet-meta__more parquet-meta__more--spektrum">
                Aktuelles aus der Welt von Wissenschaft und Forschung:
                <a {% if track_slug %}id="{{ track_slug }}.2.morelink|http://www.spektrum.de"{% endif %} href="http://www.spektrum.de" class="parquet-meta__more-link parquet-meta__more-link--spektrum">
                    Spektrum.de
                </a>
            </div>
        </div>
        <ul class="parquet-teasers">
            {% for teaser in row[:3] -%}
                {% set teaser_track_id = loop.cycle('a', 'b', 'c') %}
                {% include ["zeit.web.site:templates/inc/parquet/zon-parquet-small-spektrum.tpl"] %}
            {% endfor %}
        </ul>
    </div>
</div>
{% endprofile %}
{% endif %}
