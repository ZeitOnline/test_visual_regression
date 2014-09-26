{% block teaser %}
<article class="teaser {% block teaser_modifier %}{% endblock %}">
    {% block teaser_media_position_a %} {%endblock%}    
 
    <h2 class="teaser__heading {% block teaser_heading_modifier %}{% endblock %}}">
        {% block teaser_link %}
        <a class="teaser__combined-link" title="{{ teaser.teaserSupertitle }}- {{
        teaser.teaserTitle }}" href="{{ teaser.uniqueId }}">
            {% block teaser_kicker %}
            <span class="teaser__kicker">{{ teaser.teaserSupertitle }}</span>
            {% endblock %}
            {% block teaser_title %}
            <span class="teaser__title">{{ teaser.teaserTitle }}</span>
            {% endblock %}
        </a>
        {% endblock %}
    </h2>

    {% block teaser_media_position_b %} {% endblock %}
 
    {% block teaser_container %}
    <div class="teaser__container">
        {% block teaser_text %}
        <p class="teaser__text"> {{ teaser.teaserText }}</p>
        {% endblock %}
        {% block teaser_byline %}
        <div class="teaser__byline"> ToDo: Insert byline here </div>
        {% endblock %}
        {% block teaser_metadata %}
        <div class="teaser__metadata">
            {% block teaser_datetime %}
            <time class="teaser__datetime" datetime="2014-09-11 13:16">vor 1 Minute</time>
            {% endblock %}
            {% block commentcount%}
            <a class="teaser__commentcount" href="http://www.zeit.de/sport/2014-09/umfrage-olympische-spiele-berlin-hamburg#comments" title="9 Kommentare">9 Kommentare</a>
            {% endblock %}
        </div>
        {% endblock %}
    </div>
{% endblock %}
</article>
{% endblock %}
