{% macro footer_logo() -%}
    <a href="http://www.zeit.de/index" title="Nachrichten auf ZEIT ONLINE" class="icon-zon-logo-desktop" id="hp.global.topnav.centerpages.logo">
        <!--start: title-->Nachrichten auf ZEIT ONLINE<!--end: title-->
    </a>
{%- endmacro %}

{% macro footer_publisher(view) -%}

    {% for i in view.navigation_footer -%}
        {% set section = view.navigation_footer[i] %}

        <ul class="footer-publisher__list footer-publisher__list--is{{section.item_id}}">
            <li class="footer-publisher__item footer-publisher__item--isbold">
                {{ section.text | hide_none }}
            </li>
            {% if section.has_children() -%}
                {% for j in section -%}
                    {% set item = section[j] %}
                    <li class="footer-publisher__item">
                        <a class="footer-publisher__link" href="{{ item.href | translate_url }}">{{item.text}}</a>
                    </li>
                {%- endfor %}
            {%- endif %}
        </ul>
    {%- endfor %}

{%- endmacro %}

{% macro footer_links() -%}
    Link stuff goes here
{%- endmacro %}

{% macro footer_button(view) -%}
    <div class="icon-top-arrow"></div><a href="?">Nach oben</a>
{%- endmacro %}
