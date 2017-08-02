{# this template is shared between articles and centerpages #}

{% block wrapper_start %}
<aside class="article__item {{ self.layout() }}">
{% endblock %}

    <div class="{{ self.layout() }}__container">
        {% block debatebox_media %}{% endblock %}
        <div class="{{ self.layout() }}__right">
            <span class="{{ self.layout() }}__kicker">Debattenaufruf</span>
            <h2 class="{{ self.layout() }}__title">Müssen wir mehr über Geld sprechen?</h2>
            <p class="{{ self.layout() }}__text">
                Unbedingt! Oder doch keine gute Idee? Schicken Sie uns Ihre Texte und Erfahrungen an <a href="mailto:leser-campus@zeit.de">leser-campus@zeit.de</a>. Alle Beiträge gibt's auf unserer Serienseite zum anonymen Gehaltsprotokoll.
            </p>
        </div>
    </div>
    <a href="mailto:leser-campus@zeit.de" class="{{ self.layout() }}__button" data-ct-label="button">Schreiben Sie uns</a>
</aside>

{% block wrapper_end %}
</aside>
{% endblock %}
