{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<article class="newsteaser">
    <time class="newsteaser__time">
        {{ teaser | mod_date | format_date(pattern='HH:mm') }}
    </time>
    <div class="newsteaser__text">
        <a class="newsteaser__combined-link" title="{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }} - {{ teaser.teaserTitle or teaser.title | hide_none }}" href="{{ teaser.uniqueId | create_url }}">
            <span class="newsteaser__kicker">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</span>
            <span class="newsteaser__title">{{ teaser.teaserTitle or teaser.title | hide_none }}</span>
        </a>
        <span class="newsteaser__product">{{ teaser.product_id or teaser.product.id | hide_none }}</span>
    </div>
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
