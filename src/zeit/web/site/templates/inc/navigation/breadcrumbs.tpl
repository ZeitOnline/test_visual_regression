{% if view.breadcrumbs %}
<nav class="footer-breadcrumbs">
    <ul class="footer-breadcrumbs__list">
    {% for breadcrumb in view.breadcrumbs %}
        {% set bcrumb_text = breadcrumb[0] %}
        {% set bcrumb_link = breadcrumb[1] %}
        {% if breadcrumb[2] and breadcrumb[2] is not none %}
            {% set bcrumb_title = breadcrumb[2] %}
        {% else %}
            {% set bcrumb_title = bcrumb_text %}
        {% endif %}
        <li class="footer-breadcrumbs__item" itemtype="http://data-vocabulary.org/Breadcrumb" itemscope>
            {% if bcrumb_link is not none %}
            <a class="footer-breadcrumbs__link" itemprop="url" title="{{ bcrumb_title }}" href="{{ bcrumb_link | create_url}}" data-id="footernav.breadcrumbs.1.{{ loop.index }}.{{ bcrumb_text | format_webtrekk }}">
                <span itemprop="title">{{ bcrumb_text }}</span>
            </a>
            {% else %}{{ bcrumb_text }}{% endif %}
        </li>
    {% endfor %}
    </ul>
</nav>
{% endif %}
