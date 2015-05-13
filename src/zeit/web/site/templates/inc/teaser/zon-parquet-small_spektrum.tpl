<article class="teaser-parquet-small " data-block-type="teaser">
    {% if esi_toggle %}
        {% if teaser.image %}
        <figure class="teaser-parquet-small__media scaled-image">
            <div class="teaser-parquet-small__media-container">
                <a {% if parquet_position %}id="hp.centerpage.teaser.parquet.{{ parquet_position }}.3.{{ area_loop.cycle('a', 'b', 'c') }}.image|{{ teaser.url }}"{% endif %} class="teaser-parquet-small__media-link" title="{{ teaser.teaserTitle }}" href="{{ teaser.url }}">
                <img class="teaser-parquet-small__media-item" alt="{{ teaser.teaserTitle }}" src="{{ teaser.image | default_image_url }}">
                </a>
            </div>
        </figure>
        {% endif %}
    {% else %}
        {% set module = row %}
        {% set module_layout = 'teaser-parquet-small' %}
        {% set image = teaser.image %}
        {% if image %}
        <figure class="teaser-parquet-small__media scaled-image">
            <!--[if gt IE 8]><!-->
            <noscript data-src="{{ image | default_image_url }}">
            <!--<![endif]-->
                <div class="teaser-parquet-small__media-container">
                    <a class="teaser-parquet-small__media-link" title="{{ teaser.teaserTitle }}" href="{{ teaser.url }}">
                        <img class="teaser-parquet-small__media-item" alt="{{ image.attr_title }}" src="{{ image | default_image_url }}" data-ratio="{{ image.ratio }}">
                    </a>
                </div>
            <!--[if gt IE 8]><!-->
            </noscript>
            <!--<![endif]-->
        </figure>
        {% endif %}
    {% endif %}
    <div class="teaser-parquet-small__container ">
        <h2 class="teaser-parquet-small__heading">
            <a {% if parquet_position %}id="hp.centerpage.teaser.parquet.{{ parquet_position }}.3.{{ area_loop.cycle('a', 'b', 'c') }}.title|{{ teaser.url }}"{% endif %} class="teaser-parquet-small__combined-link" title="{{ teaser.teaserSupertitle }} - {{ teaser.teaserTitle }}" href="{{ teaser.url }}">
                <span class="teaser-parquet-small__kicker teaser-parquet-small__kicker--spektrum">{{ teaser.teaserSupertitle | hide_none }}</span>
                <span class="teaser-parquet-small__title">{{ teaser.teaserTitle | hide_none }}</span>
            </a>
         </h2>
        <p class="teaser-parquet-small__text">{{ teaser.teaserText | hide_none }}</p>
    </div>
</article>
