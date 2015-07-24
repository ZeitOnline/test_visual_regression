<ul class="breadcrumbs">
{% for breadcrumb in view.breadcrumbs %}
    {% set bcrumb_text = breadcrumb[0] %}
    {% set bcrumb_link = breadcrumb[1] %}
    {% if breadcrumb[2] is not none %}
        {% set bcrumb_title = breadcrumb[2] %}
    {% else %}
        {% set bcrumb_title = bcrumb_text %}
    {% endif %}
    <li itemtype="http://data-vocabulary.org/Breadcrumb" itemscope="itemscope">
        {% if bcrumb_link is not none %}
        <a itemprop="url" title="{{ bcrumb_title }}" href="{{ bcrumb_link }}">
            <span itemprop="title">{{ bcrumb_text }}</span>
        </a>
        {% else %}{{ bcrumb_text }}{% endif %}
    </li>
{% endfor %}
</ul>
