{% if view.storystream %}
    {% set blockname = 'storystream-in-article-teaser' %}
    <aside class="{{ blockname }} hide-lineage">
        <div class="{{ blockname }}__container">
            <div class="{{ blockname }}__content">
                <span class="{{ blockname }}__kicker">Im Überblick</span>
                <a href="#zeitleiste" class="{{ blockname }}__link"> Zeitleiste anzeigen</a>
                </h2>
            </div>
        </div>
    </aside>
{% endif %}
