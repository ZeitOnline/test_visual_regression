<aside class="{% block layout %}nextread-advertisement{% endblock %}" data-ct-area="articlebottom" data-ct-row="{{ teaser.supertitle }}-nextread">
    <span class="{{ self.layout() }}__label">{{ {'publisher': 'Verlagsangebot', 'advertisement': 'Anzeige'}.get(teaser.supertitle) }}</span>

    <div class="{{ self.layout() }}__container">

        <div class="{{ self.layout() }}__media"></div>

        <h2 class="{{ self.layout() }}__title">{{ teaser.title }}</h2>
        <p class="{{ self.layout() }}__text">{{ teaser.text }}</p>

        <a class="{{ self.layout() }}__button" title="{{ teaser.title }}: {{ teaser.text }}" href="{{ teaser.url }}" data-ct-column="button">{{- teaser.button_text -}}</a>

    </div>
</aside>
