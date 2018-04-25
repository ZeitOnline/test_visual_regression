{%- import 'zeit.web.campus:templates/macros/layout_macro.tpl' as lama -%}
<aside class="{% block layout %}teaser-follow-us{% endblock %} {% if module.visible_mobile == False %} mobile-hidden{% endif %}"
    data-unique-id="{{ teaser.uniqueId }}"
    data-meetrics="{{ area.kind }}">
    <div class="{{ self.layout() }}__packshot">
        <a class="packshot" href="{{ teaser | create_url | append_campaign_params }}" title="
            {{- teaser.teaserSupertitle or teaser.supertitle -}}: {{ teaser.teaserTitle or teaser.title }}" data-ct-label="packshot">
            {% set module_layout = "packshot" %}
            {% include "zeit.web.campus:templates/inc/teaser/asset/image_zco-follow-us.tpl" %}
            <div class="packshot__content">
                <div class="packshot__kicker">{{- teaser.teaserSupertitle or teaser.supertitle -}}</div>
                <div class="packshot__title">{{ teaser.teaserTitle or teaser.title }}</div>
                <div class="packshot__cta">{{ lama.use_svg_icon('arrow-right', 'packshot__arrow', view.package) }} Jetzt bestellen</div>
            </div>
        </a>
    </div>
    <div class="{{ self.layout() }}__actions">
        <a class="abo-cta" href="{{ settings('community_profile_url', '') }}/newsletter-signup?nl=campus" data-ct-label="newsletter">
            <div class="abo-cta__text">Hol’ Dir ZEIT Campus in dein Postfach</div>
            <span class="abo-cta__label">
                <span class="visually-hidden">Jetzt den ZEIT Campus Newsletter </span>Abonnieren
            </span>
        </a>
        <a class="follow-us" href="https://de-de.facebook.com/zeitcampus" data-ct-label="facebook">
            <div class="follow-us__logo">{{ lama.use_svg_icon('facebook', 'follow-us__facebook', view.package) }}</div>
            <div class="follow-us__text">Folgt uns unauffällig</div>
        </a>
    </div>
</aside>
