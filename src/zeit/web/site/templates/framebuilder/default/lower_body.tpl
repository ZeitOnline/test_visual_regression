                {{ lama.adplace(view.banner(8), view, mobile=True) }}
            </main>
            {% block footer %}
                {%- include "zeit.web.site:templates/inc/footer.html" ignore missing -%}
            {% endblock footer %}
        </div>
    </div>
    {% include "zeit.web.core:templates/inc/ads/finalize.html" ignore missing %}
    {% if view.framebuilder_requires_webtrekk %}
        {% include "zeit.web.core:templates/inc/tracking/webtrekk.html" ignore missing %}
    {% endif %}
    {% include "zeit.web.core:templates/inc/tracking/celera_one.html" ignore missing %}
    <script>
        var require = { baseUrl: '{{ request.asset_host }}/js/' };
    </script>

    <script src="{{ request.asset_host }}/js/site.js"></script>

</body>
</html>
