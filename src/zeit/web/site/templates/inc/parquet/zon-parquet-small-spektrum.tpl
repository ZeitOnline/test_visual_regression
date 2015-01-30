<article class="teaser-parquet-small " data-block-type="teaser">
    <figure class="teaser-parquet-small__media scaled-image">
        <div class="teaser-parquet-small__media-container">
            <a class="teaser-parquet-small__media-link" title="{{teaser.teaserTitle}}" href="{{teaser.url}}">
                <img class="teaser-parquet-small__media-item" alt="{{teaser.teaserTitle}}" src="{{teaser.image | default_image_url}}">
            </a>
        </div>
    </figure>
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
