{% if view.storystream %}

    {% set blockname = 'storystream-in-article' %}

    <aside class="{{ blockname }} hide-lineage" id="zeitleiste">
        <div class="{{ blockname }}__container {{ blockname }}__container--header">
            <div class="{{ blockname }}__content {{ blockname }}__content--header {{ blockname }}__content--with-border">
                <h2 class="{{ blockname }}__headline">
                    <span class="{{ blockname }}__kicker">Im Überblick</span><span class="visually-hidden">: </span>
                    <span class="{{ blockname }}__title">{{ view.storystream.title }}</span>
                </h2>
            </div>
        </div>
        <div class="{{ blockname }}__container">
            <div class="{{ blockname }}__content {{ blockname }}__content--with-border">
                <ul class="{{ blockname }}__list">
                    {% for atom in view.storystream_items %}

                        {% if atom == view.context %}
                            <li class="{{ blockname }}__listcaption {{ blockname }}__listcaption--current">Dieser Artikel</li>
                            <li class="{{ blockname }}__listitem {{ blockname }}__listitem--current">
                                {{ atom.tldr_title or atom.teaserTitle or atom.title }}</a>
                            </li>

                            {% if not loop.last %}
                                <li class="{{ blockname }}__listcaption">zuvor</li>
                            {% endif %}

                        {% else %}

                            {% if loop.first %}
                                <li class="{{ blockname }}__listcaption">danach</li>
                            {% endif %}

                            <li class="{{ blockname }}__listitem">
                            <a href="{{ atom.uniqueId | create_url }}" class="{{ blockname }}__link" data-id="article-storystreamteaser.bottom.link..">{{ atom.tldr_title or atom.title
or atom.teaserTitle or atom.title }}
                            </a></li>
                        {% endif %}
                    {% endfor %}
                </ul>
            </div>
            <div class="{{ blockname }}__content {{ blockname }}__content--footer">
                <a class="button" href="{{ view.storystream.uniqueId | create_url }}" data-id="article-storystreamteaser.bottom.button..">zum Live-Dossier</a>
            </div>
        </div>
    </aside>
{% endif %}
