<article class="{% block layout %}teaser-border{% endblock %}" data-unique-id="{{ read_more_url }}" data-meetrics="{{ area.kind }}" data-clicktracking="{{ area.kind }}">
    <div class="{{ self.layout() }}__container">
        <a class="{{ self.layout() }}__link" href="{{ read_more_url | create_url | append_campaign_params }}">
            <h2 class="{{ self.layout() }}__heading">
                {{- area.read_more | default('Alle Themen', true) -}}
            </h2>
        </a>
    </div>
</article>
