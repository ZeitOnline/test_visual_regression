{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<article class="newsteaser">
    <a class="newsteaser__combined-link" title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}" href="{{ teaser.uniqueId | create_url }}">
        <time class="newsteaser__time">
            {{ teaser | mod_date | format_date(pattern='HH:mm') }}
        </time>
        <span class="newsteaser__text">
            <span class="newsteaser__kicker">{{ teaser.teaserSupertitle or teaser.supertitle }}</span>
            <span class="newsteaser__title">{{ teaser.teaserTitle or teaser.title }}</span>
            <span class="newsteaser__product">{{ teaser.product.title }}</span>
        </span>
    </a>
</article>

{# only include ads on /news/index page, NOT on home page #}
{% if view.banner_on and area.kind == 'overview' and layout == 'zon-newsteaser' -%}
    {% if loop.index == 10 %}
        <div class="newsteaser__ad">
            {{ lama.adplace(view.banner(7), view) }}
            {{ lama.adplace(view.banner(4), view, mobile=True) }}
        </div>
    {% elif loop.index == 30 %}
        <div class="newsteaser__ad">
            {{ lama.adplace(view.banner(8), view) }}
        </div>
    {% endif %}
{% endif %}
