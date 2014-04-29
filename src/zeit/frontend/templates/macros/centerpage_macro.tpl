
{% macro include_cp_block(obj, ad) -%}
    {% for teaser_block in obj -%}
        {%-
            set teaser_blocks = [
                'templates/inc/teaser_block_' + teaser_block.layout.id + '.html',
                'templates/inc/teaser_block_default.html'
            ]
        %}
        {% include teaser_blocks ignore missing %}

        {% if (ad == 'enable') and (loop.index == 2 or loop.last) and (added is not defined) -%}
            <!-- special ad integration by counter -->
            {% set added = true %}
            {% include 'templates/inc/teaser/teaser_ad.html' ignore missing %}
        {% endif %}

    {% endfor %}
{%- endmacro %}