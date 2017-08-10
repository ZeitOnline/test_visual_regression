<aside class="{% block layout %}nextread-advertisement{% endblock %}">
    <span class="{{ self.layout() }}__label">Verlagsangebot</span>

    <div class="{{ self.layout() }}__container">

        <div class="{{ self.layout() }}__media"></div>

        <h2 class="{{ self.layout() }}__title">Stellenangebote in Wirtschaft und Lehre</h2>
        <p class="{{ self.layout() }}__text">Entdecken Sie Jobs mit Perspektive im ZEITStellenmarkt.</p>

        <a class="{{ self.layout() }}__button" href="http://jobs.zeit.de/action/account/create/agent-all?wt_zmc=fix.int.zonpmr.zeitde.stellenmarkt.funktionsbox.streifen.startseite.&amp;utm_medium=fix&amp;utm_source=zeitde_zonpmr_int&amp;utm_campaign=stellenmarkt&amp;utm_content=funktionsbox_streifen_startseite_">Jobs finden</a>

    </div>
</aside>

{#
{% set image = get_image(module, variant_id='super', fallback=False) %}
{% set href = teaser.url %}
{% set module_layout = 'nextread-advertisement' %}
{% set tracking_slug = 'articlebottom.publisher-nextread...' %}

<article class="{{ module_layout }}">
    <span class="{{ module_layout }}__label">{{ {'publisher': 'Verlagsangebot', 'advertisement': 'Anzeige'}.get(teaser.supertitle) }}</span>
    <div class="{{ module_layout }}__container-outer">
        <div class="{{ module_layout }}__container-inner">
            <h2 class="{{ module_layout }}__title">{{ teaser.title }}</h2>
            <p class="{{ module_layout }}__text">{{ teaser.text }}</p>
            {% include "zeit.web.core:templates/inc/asset/image_nextad.tpl" %}
            <a class="{{ module_layout }}__button" title="{{ teaser.title }}: {{ teaser.text }}" href="{{ teaser.url }}" style="background-color:#{{ teaser.button_color }}" data-id="{{ tracking_slug }}button">
                {{- teaser.button_text -}}
            </a>
        </div>
    </div>
</article>
#}
