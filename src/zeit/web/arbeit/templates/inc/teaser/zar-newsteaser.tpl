<article class="newsteaser" data-meetrics="{{ area.kind }}">
    <a class="newsteaser__combined-link" title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}" href="{{ teaser.uniqueId | create_url }}">
        <time class="newsteaser__time">
           {{ teaser | mod_date | format_date(pattern='HH:mm', type='switch_from_hours_to_date' if cp_type in ['autotopic', 'manualtopic'] else '') }}
        </time>
        <div class="{{ 'newsteaser__text' | with_mods('on-' ~ cp_type if cp_type in ['autotopic', 'manualtopic']) }}">
            <h2 class="newsteaser__heading">
                {%- if teaser.teaserSupertitle or teaser.supertitle -%}
                    <span class="newsteaser__kicker">
                        {{- teaser.teaserSupertitle or teaser.supertitle -}}
                    </span><span class="visually-hidden">: </span>
                {% endif -%}
                <span class="newsteaser__title">{{ teaser.teaserTitle or teaser.title }}</span>
            </h2>
            <span class="newsteaser__product">{{ teaser.product.title }}</span>
        </div>
    </a>
</article>
