{% macro footer_logo(request) -%}
    <a href="http://{{ request.host }}/index" title="Nachrichten auf ZEIT ONLINE" class="icon-zon-logo-desktop" data-id="footernav.logo.1..logo">
        <!--start: title-->Nachrichten auf ZEIT ONLINE<!--end: title-->
    </a>
{%- endmacro %}

{% macro footer_publisher(view) -%}
    {{ build_footer_bar(view.navigation_footer_publisher, 'publisher', True) }}
{%- endmacro %}

{% macro footer_links(view) -%}
    {{ build_footer_bar(view.navigation_footer_links, 'links') }}
{%- endmacro %}

{% macro build_footer_bar(navigation, class, publisher=False) -%}
    {% for i in navigation -%}
        {% set section = navigation[i] %}

        {% if (loop.index == 1) or (publisher and loop.index % 2 == 0) or (not publisher and loop.index % 2 == 1) -%}
        <div class="footer-{{ class }}__row">
        {%- endif %}

            <ul class="footer-{{ class }}__list">
                {% if section.text -%}
                <li class="footer-{{ class }}__item footer-{{ class }}__item--label">
                    {{ section.text | hide_none }}
                </li>
                {%- endif %}

                {% if section.has_children() -%}
                    {% for j in section -%}
                        {% set item = section[j] -%}
                        <li class="footer-{{ class }}__item">
                            <a class="footer-{{ class }}__link" href="{{ item.href }}"  itemprop="url" data-id="{{ item.item_id if item.item_id }}"><span itemprop="name">{{ item.text }}</span></a>
                        </li>
                    {%- endfor %}
                {%- endif %}
            </ul>

        {% if (publisher and loop.index % 2 == 1) or (not publisher and loop.index % 2 == 0) -%}
        </div>
        {%- endif %}

        {% if publisher and section.item_id == 'first' %}
        <a href="#" class="footer-{{ class }}__more" data-id="footernav.mehr.1..more">Mehr</a>
        {% endif %}
    {%- endfor %}
{%- endmacro %}
