{% macro footer_logo() -%}
    <a href="http://www.zeit.de/index" title="Nachrichten auf ZEIT ONLINE" class="icon-zon-logo-desktop" id="hp.global.topnav.centerpages.logo">
        <!--start: title-->Nachrichten auf ZEIT ONLINE<!--end: title-->
    </a>
{%- endmacro %}

{% macro footer_publisher(view) -%}
    {{ build_footer_bar(view.navigation_footer_publisher,'publisher',true) }}
{%- endmacro %}

{% macro footer_links(view) -%}
    {{ build_footer_bar(view.navigation_footer_links,'links') }}
{%- endmacro %}

{% macro build_footer_bar(navigation,class,more) -%}
    {% for i in navigation -%}
        {% set section = navigation[i] %}
        <div class="footer-{{class}}__inner footer-{{class}}__inner--is{{section.item_id}}">
            <ul class="footer-{{class}}__list footer-{{class}}__list--is{{section.item_id}}">
                <li class="footer-{{class}}__item footer-{{class}}__item--isbold">
                    {{ section.text | hide_none }}
                </li>
                {% if section.has_children() -%}
                    {% for j in section -%}
                        {% set item = section[j] %}
                        <li class="footer-{{class}}__item">
                            <a class="footer-{{class}}__link" href="{{ item.href | translate_url }}">{{item.text}}</a>
                        </li>
                    {%- endfor %}
                {%- endif %}
            </ul>
        </div>
        {% if more and section.item_id == 'first' %}
            <div class="footer-{{class}}__more">
                <a href="#">Mehr</a>
            </div>
        {% endif %}
    {%- endfor %}
{%- endmacro %}
