<article class="teaser-small">
    {% set image = get_image(module, teaser, fallback=False) %}
    {% if image %}
        {% set source = request.image_host + image.path %}
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
