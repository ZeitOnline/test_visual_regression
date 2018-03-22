            </main>
            {% block adplace_floor %}
                {% if not view.is_hp -%}
                    <!-- P7 -->
                    {% include "zeit.web.core:templates/inc/ads/places/desktop/place16.html" %}
                {% endif -%}
                {% include "zeit.web.core:templates/inc/ads/places/mobile/place8.html" %}
            {% endblock adplace_floor %}
            {% block footer %}
                {%- include "zeit.web.site:templates/inc/footer.html" -%}
            {% endblock footer %}
        </div>
    </div>
    {% include "zeit.web.core:templates/inc/ads/finalize.html" %}
    {% if view.framebuilder_requires_webtrekk %}
        {% include "zeit.web.core:templates/framebuilder/inc/webtrekk-inline-ssoid.html" %}
        {% include "zeit.web.core:templates/inc/tracking/webtrekk.html" %}
    {% endif %}
    {% if view.framebuilder_requires_meetrics %}
        {% include "zeit.web.core:templates/inc/tracking/meetrics.html" %}
    {% endif %}

    {% block additional_frame_elements %}
    {% include "zeit.web.core:templates/inc/inline_js/app_wrapper.html" %}

    <script src="{{ request.asset_host }}/js/web.site/frame.js"></script>
    {% endblock additional_frame_elements %}

</body>
</html>
