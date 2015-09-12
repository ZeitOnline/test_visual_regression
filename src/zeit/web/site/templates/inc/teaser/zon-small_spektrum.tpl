<article class="teaser-small">
    {% if esi_toggle %}
        {% if teaser.image %}
        <figure class="teaser-small__media scaled-image">
            <div class="teaser-small__media-container">
                <a {% if parquet_position %}id="hp.centerpage.teaser.parquet.{{ parquet_position }}.3.{{ module_loop.cycle('a', 'b', 'c') }}.image|{{ teaser.url }}"{% endif %} class="teaser-small__media-link" title="{{ teaser.teaserTitle }}" href="{{ teaser.url }}">
                <img class="teaser-small__media-item" alt="{{ teaser.teaserTitle }}" src="{{ teaser.image | default_image_url }}">
                </a>
            </div>
        </figure>
        {% endif %}
    {% else %}
        {% set module = row %}
        {% set module_layout = 'teaser-small' %}
        {% set image = teaser.image %}
        {% if image %}
            {% set source = image | default_image_url %}
        <figure class="teaser-small__media scaled-image">
            <!--[if gt IE 8]><!-->
            <noscript data-src="{{ source }}">
            <!--<![endif]-->
                <div class="teaser-small__media-container">
                    <a class="teaser-small__media-link" title="{{ teaser.teaserTitle }}" href="{{ teaser.url }}">
                        <img class="teaser-small__media-item" alt="{{ image.attr_title }}" src="{{ source }}" data-src="{{ source }}" data-ratio="{{ image.ratio }}">
                    </a>
                </div>
            <!--[if gt IE 8]><!-->
            </noscript>
            <!--<![endif]-->
        </figure>
        {% endif %}
    {% endif %}
    <div class="teaser-small__container ">
        <h2 class="teaser-small__heading">
            <a {% if parquet_position %}id="hp.centerpage.teaser.parquet.{{ parquet_position }}.3.{{ module_loop.cycle('a', 'b', 'c') }}.title|{{ teaser.url }}"{% endif %} class="teaser-small__combined-link" title="{{ teaser.teaserSupertitle }} - {{ teaser.teaserTitle }}" href="{{ teaser.url }}">
                <span class="teaser-small__kicker teaser-small__kicker--spektrum">{{ teaser.teaserSupertitle | hide_none }}</span>
                <span class="teaser-small__title">{{ teaser.teaserTitle | hide_none }}</span>
            </a>
         </h2>
        <p class="teaser-small__text">{{ teaser.teaserText | hide_none }}</p>
    </div>
</article>
