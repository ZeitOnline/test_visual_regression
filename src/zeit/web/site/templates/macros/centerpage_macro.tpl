{% macro include_teaser_datetime(teaser, layout='', kind='') -%}
    {%- if kind == 'ranking' or kind == 'nextread' or kind.startswith('author') -%}
        {%- set time = teaser | release_date | format_timedelta(days=3, absolute=True) | title -%}
    {%- elif kind == 'teaser-storystream' -%}
        {%- set time = teaser | mod_date | format_timedelta(days=3) -%}
    {%- else -%}
        {%- set time = get_delta_time_from_article(teaser) -%}
    {%- endif -%}

    {%- if time -%}
        {% if kind == 'nextread' or kind == 'teaser-storystream' %}
            <span class="{{ layout }}__dt">
                {{ time }}
            </span>
        {% else %}
            <time class="{{ layout }}__datetime js-update-datetime" datetime="{{ teaser | release_date | format_date('iso8601') }}">
                {{ time }}
            </time>
        {% endif %}
    {%- endif %}
{%- endmacro %}

{% macro section_heading(title, label='', path=None, view=None, tracking_slug=None, unpadded=None) -%}
    <div class="section-heading {% if unpadded %}section-heading--unpadded{% endif %}">
        <h3 class="section-heading__title">{{ title }}</h3>
        {% if path -%}
        <a href="{% if view %}{{ view.request.route_url('home') }}{% endif %}{{ path }}"
           class="section-heading__link {% if unpadded %}section-heading__link--unpadded{% endif %}"
            {%- if tracking_slug %} data-id="{{ tracking_slug }}"{% endif %}>
            <span class="section-heading__text">{{ label }}</span>
        </a>
        {%- endif %}
    </div>
{%- endmacro %}
