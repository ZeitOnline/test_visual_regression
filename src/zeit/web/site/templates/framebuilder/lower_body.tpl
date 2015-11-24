                {{ lama.adplace(view.banner(8), view, mobile=True) }}
            </main>
            <footer class="footer" role="contentinfo" itemscope="itemscope" itemtype="http://schema.org/SiteNavigationElement" >
                {% block footer %}
                    {%- include "zeit.web.site:templates/inc/footer.html" ignore missing -%}
                {% endblock footer %}
            </footer>
        </div>
    </div>
    {% include "zeit.web.core:templates/inc/ads/finalize.html" ignore missing %}
    {% include "zeit.web.core:templates/inc/tracking/webtrekk.html" ignore missing %}
    <script>
        var require = { baseUrl: '{{ request.asset_host }}/js/' };
    </script>

    <script src="{{ request.asset_host }}/js/site.js"></script>

</body>
</html>
