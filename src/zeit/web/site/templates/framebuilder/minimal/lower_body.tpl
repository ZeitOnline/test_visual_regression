                {{ lama.adplace(banner(8), view, mobile=True) }}
            </main>
            {% block footer -%}
                {%- include "zeit.web.site:templates/inc/footer.html" -%}
            {%- endblock footer %}
        </div>
    </div>
    {% include "zeit.web.core:templates/inc/ads/finalize.html" %}
    {% if view.framebuilder_requires_webtrekk %}
        {% include "zeit.web.core:templates/inc/tracking/webtrekk.html" %}
    {% endif %}
    {% if view.framebuilder_requires_meetrics %}
        {% include "zeit.web.core:templates/inc/tracking/meetrics.html" %}
    {% endif %}

</body>
</html>
