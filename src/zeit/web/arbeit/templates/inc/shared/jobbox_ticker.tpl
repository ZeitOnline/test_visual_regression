<aside class="{% block layout %}jobbox-ticker{% endblock %} js-jobbox-animation {% block layout_modifier %}{% endblock %}">
    <span class="{{ self.layout() }}__label">Verlagsangebot</span>

    <div class="{{ self.layout() }}__heading">
        <span class="{{ self.layout() }}__kicker">ZEIT Stellenmarkt</span>
        <h2 class="{{ self.layout() }}__title">{{ jobbox.teaser_text }}</h2>
        <a class="{{ self.layout() }}__link" href="{{ jobbox.landing_page_url }}">Zur Stellenliste.</a>
    </div>

    {% if jobitems %}
        <div class="{{ self.layout() }}-item__container js-jobbox-animation__container">
            <span class="{{ self.layout() }}-item__kicker">Aktuelle Jobs</span>
            <ul class="{{ self.layout() }}-item__list">
                {% for jobitem in jobitems %}
                <li class="{{ self.layout() }}-item js-jobbox-animation__jobitem">
                    <h3 class="{{ self.layout() }}-item__title">{{ jobitem.title }}</h3>
                    <span class="{{ self.layout() }}-item__text">{{ jobitem.text }}</span>
                    <a class="{{ self.layout() }}-item__link" href="{{ jobitem.url }}">Zum Jobangebot</a>
                </li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}
</aside>
