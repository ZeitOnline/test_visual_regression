
<div class="buzzboard__container">
    <h2 class="buzzboard__heading ">
        <a class="buzzboard__combined-link" title="{{ teaser.teaserTitle or teaser.title }}" href="{{ teaser.uniqueId | create_url }}">
            <span class="buzzboard__kicker">
                {{ teaser.supertitle }}
            </span>
            <span class="buzzboard__title">
                {{ teaser.teaserTitle or teaser.title }}
            </span>
        </a>
    </h2>
    <span class="buzzboard__metadata">
       {{ (teaser.score * module.score_factor) | round | pluralize(*module.score_pattern) }}
    </span>
</div>
