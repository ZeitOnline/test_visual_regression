{% if view.breadcrumbs %}
<nav class="footer-breadcrumbs">
    <ul class="footer-breadcrumbs__list" itemscope itemtype="http://schema.org/BreadcrumbList">
    {%- for breadcrumb in view.breadcrumbs -%}
        {%- set text = breadcrumb[0] -%}
        {%- set link = breadcrumb[1] -%}
        <li class="footer-breadcrumbs__item" itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem">
            {%- if link is not none -%}
            <a class="footer-breadcrumbs__link" itemprop="item" title="
                {{- breadcrumb[2] | default(text, True) }}" href="
                {{- link | create_url }}" data-id="footernav.breadcrumbs.1.{{ loop.index }}.{{ text | format_webtrekk -}}
                "><span itemprop="name">{{ text }}</span></a>
            {%- else -%}
                <span itemprop="name">{{ text }}</span>
            {%- endif -%}
            <meta itemprop="position" content="{{ loop.index }}">
        </li>
    {% endfor %}
    </ul>
</nav>
{% endif %}
