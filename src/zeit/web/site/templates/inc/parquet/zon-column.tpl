{%- extends "zeit.web.site:templates/inc/parquet/zon-parquet-small.tpl" -%}

{% block teaser_media_position_before_title %}
    <div class="teaser-parquet-small__label">Kolumne: {{ teaser.serie.serienname }}</div>
    {{ super() }}
{% endblock %}
