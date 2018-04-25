{% if view.storystream %}
    {% set blockname = 'storystream-in-article-teaser' %}
    <aside class="{{ blockname }}">
        <div class="{{ blockname }}__content">
            <span class="{{ blockname }}__kicker">Im Überblick</span>
            <a href="#zeitleiste" class="{{ blockname }}__link js-scroll" data-id="article-storystreamteaser.head.link..">Zeitleiste anzeigen</a>
        </div>
    </aside>
{% endif %}
