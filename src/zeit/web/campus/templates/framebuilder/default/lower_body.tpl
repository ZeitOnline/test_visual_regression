                {{ lama.adplace(view.banner(8), view, mobile=True) }}
            </main>
            {% block footer %}
                {%- include "zeit.web.campus:templates/inc/footer.html" -%}
            {% endblock footer %}
        </div>
    </div>
    {% include "zeit.web.core:templates/inc/ads/finalize.html" %}
    {% if view.framebuilder_requires_webtrekk %}
        {% include "zeit.web.core:templates/inc/tracking/webtrekk.html" %}
    {% endif %}
    {% if view.framebuilder_requires_meetrics %}
        {% include "zeit.web.core:templates/inc/tracking/meetrics.html" ignore missing %}
    {% endif %}
    {% include "zeit.web.core:templates/inc/inline_js/app_wrapper.html" %}

    <script>
        var require = { baseUrl: '{{ request.asset_host }}/js/' };
    </script>
    <script src="{{ request.asset_host }}/js/campus.js"></script>

</body>
</html>
