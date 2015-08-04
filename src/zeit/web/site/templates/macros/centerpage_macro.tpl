{% macro include_teaser_datetime(teaser, layout='', kind='') -%}
    <time class="{{ layout }}__datetime js-update-datetime" datetime="{{ teaser | mod_date | format_date('iso8601') }}">
    {%- if kind == 'ranking' -%}
        {{ teaser | mod_date | format_timedelta(days=3, absolute=True) | title }}
    {%- elif kind == 'nextread' -%}
        {{ teaser | mod_date | format_timedelta(days=356, absolute=True) | title }}
    {%- else -%}
        {{ get_delta_time_from_article(teaser) | hide_none }}
    {%- endif -%}
    </time>
{%- endmacro %}

{% macro image_copyright(copyright, blockname) -%}
    {%- if copyright[0][1] -%}
        <a class="{{ blockname }}__link" href="{{ copyright[0][1] }}" target="_blank">
    {%- endif -%}
            <span class="{{ blockname }}__item">©&nbsp;{{ copyright[0][0] | replace('© ', '') }}</span>
    {%- if copyright[0][1] -%}
        </a>
    {%- endif -%}
{%- endmacro %}

{% macro section_heading(title, label='', path=None, view=None, tracking_slug=None) -%}
    <div class="section-heading">
        <h3 class="section-heading__title">{{ title }}</h3>
        {% if path -%}
        <a href="{% if view %}{{ view.request.route_url('home') }}{% endif %}{{ path }}" class="section-heading__link"
            {%- if tracking_slug %} data-id="{{ tracking_slug }}"{% endif %}>
            <span class="section-heading__text">{{ label }}</span>
        </a>
        {%- endif %}
    </div>
{%- endmacro %}
