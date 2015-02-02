<article class="teaser-parquet-small " data-block-type="teaser">
    {% if esi_toggle %}
        {% if teaser.image %}
        <figure class="teaser-parquet-small__media scaled-image">
            <div class="teaser-parquet-small__media-container">
                <a class="teaser-parquet-small__media-link" title="{{teaser.teaserTitle}}" href="{{teaser.url}}">
                <img class="teaser-parquet-small__media-item" alt="{{teaser.teaserTitle}}" src="{{teaser.image | default_image_url}}">
                </a>
            </div>
        </figure>
        {% endif %}
    {% else %}
        {% set teaser_block = row %}
        {% set teaser_block_layout = 'teaser-parquet-small' %}
        {% set image = teaser.image %}
        {% if image %}
        <figure class="teaser-parquet-small__media scaled-image">
            <!--[if gt IE 8]><!-->
            <noscript data-src="{{ image | default_image_url }}">
            <!--<![endif]-->
                <div class="teaser-parquet-small__media-container">
                    <a class="teaser-parquet-small__media-link" title="{{teaser.teaserTitle}}" href="{{teaser.url}}">
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
            <a class="teaser-parquet-small__combined-link" title="{{teaser.teaserSupertitle}} - {{teaser.teaserTitle}}" href="{{teaser.url}}">
                <span class="teaser-parquet-small__kicker teaser-parquet-small__kicker--spektrum">{{teaser.teaserSupertitle}}</span>
                <span class="teaser-parquet-small__title">{{teaser.teaserTitle}}</span>
            </a>
         </h2>
        <p class="teaser-parquet-small__text">{{teaser.teaserText}}</p>
    </div>
</article>