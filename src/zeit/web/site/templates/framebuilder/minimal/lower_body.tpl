                {{ lama.adplace(view.banner(8), view, mobile=True) }}
            </main>
            {% block footer -%}
                {%- include "zeit.web.site:templates/inc/footer.html" ignore missing -%}
            {%- endblock footer %}
        </div>
    </div>
    {% include "zeit.web.core:templates/inc/ads/finalize.html" ignore missing %}
    {% if view.framebuilder_requires_webtrekk %}
        {% include "zeit.web.core:templates/inc/tracking/webtrekk.html" ignore missing %}
    {% endif %}
    {% if view.framebuilder_requires_meetrics %}
        {% include "zeit.web.core:templates/inc/tracking/meetrics.html" ignore missing %}
    {% endif %}

</body>
</html>
