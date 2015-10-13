{% macro footer_logo(request) -%}
    <a href="http://{{ request.host }}/index" title="Nachrichten auf ZEIT ONLINE" class="icon-zon-logo-desktop" data-id="footernav.logo.1..logo">
        <!--start: title-->Nachrichten auf ZEIT ONLINE<!--end: title-->
    </a>
{%- endmacro %}

{% macro footer_publisher(view) -%}
    {{ build_footer_bar(view, view.navigation_footer_publisher, 'publisher', True) }}
{%- endmacro %}

{% macro footer_links(view) -%}
    {{ build_footer_bar(view, view.navigation_footer_links, 'links') }}
{%- endmacro %}

{% macro build_footer_bar(view, navigation, class, publisher=False) -%}
    {% for i in navigation -%}
        {% set section = navigation[i] %}
        {% set row_loop = loop %}

        {% if (loop.index == 1) or (publisher and loop.index % 2 == 0) or (not publisher and loop.index % 2 == 1) -%}
        <div class="footer-{{ class }}__row{% if publisher and loop.index > 1 %} footer-{{ class }}__row--extra{% endif %}">
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

                        {# "Bildrechte" is done manually ...
                            /zeit.web/src/zeit/web/core/data/config/navigation-footer-links.xml does not work !? #}
                        {% if view.type == 'centerpage' and class == 'links' and row_loop.index == 2 and loop.index == 1 %}
                            <li class="footer-{{ class }}__item">
                                <a class="footer-{{ class }}__link js-image-copyright-footer" href="#" data-id="footernav.bottom.2.0.bildrechte">Bildrechte</a>
                            </li>
                        {% endif %}

                        <li class="footer-{{ class }}__item">
                            <a class="footer-{{ class }}__link" href="{{ item.href }}"  itemprop="url" data-id="{{ item.item_id if item.item_id }}"><span itemprop="name">{{ item.text }}</span></a>
                        </li>
                    {%- endfor %}
                {%- endif %}
            </ul>

        {% if (loop.last) or (publisher and loop.index % 2 == 1) or (not publisher and loop.index % 2 == 0) -%}
        </div>
        {%- endif %}

        {% if publisher and section.item_id == 'first' %}
        <div class="footer-{{ class }}__row footer-{{ class }}__row--more">
            <a href="#" class="footer-{{ class }}__more" data-id="footernav.mehr.1..more">Mehr</a>
        </div>
        {% endif %}
    {%- endfor %}
{%- endmacro %}
