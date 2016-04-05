{%- import 'zeit.web.campus:templates/macros/layout_macro.tpl' as lama -%}
{#
uses nearly nothing from default teaser, so does not extend it,
there are however some unsolved challenges:
- clicktracking (and meetrics?) has to be provided for each block
- there is not one test
#}
<aside class="{% block layout %}teaser-follow-us{% endblock %} {% block teaser_modifier %}{% endblock %}{% if module.visible_mobile == False %} mobile-hidden{% endif %}"
    data-unique-id="{{ teaser.uniqueId }}"
    {% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
    data-clicktracking="{{ area.kind }}"
    {% block teaser_attributes %}{% endblock %}>
    <div class="{{ self.layout() }}__packshot">
        <a class="packshot" href="{{ teaser | create_url | append_campaign_params }}" title="{{- teaser.teaserSupertitle or teaser.supertitle -}}: {{ teaser.teaserTitle or teaser.title }}">
            {% set module_layout = "packshot" %}
            {% include "zeit.web.campus:templates/inc/teaser/asset/image_zco-follow-us.tpl" ignore missing %}
            <div class="packshot__content">
                <div class="packshot__kicker">{{- teaser.teaserSupertitle or teaser.supertitle -}}</div>
                <div class="packshot__title">{{ teaser.teaserTitle or teaser.title }}</div>
                <div class="packshot__cta">{{ lama.use_svg_icon('arrow-right', 'toolbox__arrow', request) }} Jetzt bestellen</div>
            </div>
        </a>
    </div>
    <div class="{{ self.layout() }}__actions">
        <div class="abo-cta">
            <div class="abo-cta__text">Abonnieren Sie den ZEIT CAMPUS Newsletter</div>
            <a class="abo-cta__label" href="http://link_zum_newsletter.com">
                Abonnieren
            </a>
        </div>
        <a class="follow-us" href="http://folgend_sie_uns">
            <div class="follow-us__logo">{{ lama.use_svg_icon('facebook', 'follow-us__facebook', request) }}</div>
            <div class="follow-us__text">Folgen Sie uns auf Facebook</div>
        </a>
    </div>
</aside>
