{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama %}
{% import 'zeit.web.arbeit:templates/macros/centerpage_macro.tpl' as cp %}

{% block teaser %}
<article class="
    {%- block layout %}{{ layout | default('default') }}{% endblock %} {% block teaser_modifier %}{% endblock %}
    {%- if teaser.product.title == 'Advertorial' and not view.is_advertorial %} {{ self.layout() }}--advertorial{% endif %}
    {%- if module.visible_mobile == False %} mobile-hidden{% endif %}" data-unique-id="
    {{- teaser.uniqueId }}"
    {%- block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
    {%- block zplus_data %}{% if teaser is zplus_content %} data-zplus="zplus{% if teaser is zplus_registration_content %}-register{% endif %}"{% endif %}{% endblock %} itemscope itemtype="http://schema.org/Article" itemref="publisher">

    {% block teaser_allcontent %}

    {% block teaser_label %}{% endblock %}
    {% block teaser_media %}{% endblock %}

    <div class="{{ self.layout() }}__container">

        {% block teaser_heading %}
            <h2 class="{{ self.layout() }}__heading {% block teaser_heading_modifier %}{% endblock %}">
                {% block teaser_link %}
                <a class="{{ self.layout() }}__combined-link"
                   title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}"
                   href="{{ teaser | create_url | append_campaign_params }}"
                   {%- block teaser_additional_attribute_for_textlink %}{% endblock %}>
                    {% block teaser_kicker %}
                        {#- We need to strip all the template whitespeces within this block, hence all the whitespace control chars.
                        Whitespace control even needs to be applied for template commments. -#}
                        {%- if teaser.teaserSupertitle or teaser.supertitle  or teaser is zplus_abo_content or (teaser is zplus_registration_content and toggles('zplus_badge_gray')) -%}
                            <span class="{{ '%s__kicker' | format(self.layout()) | with_mods('leserartikel' if teaser is leserartikel) }}">
                                {%- block zplus_kicker_logo -%}
                                    {%- if teaser is zplus_abo_content -%}
                                        {{- lama.use_svg_icon('zplus', 'zplus-logo zplus-logo--s svg-symbol--hide-ie', view.package, a11y=False) -}}
                                    {%- elif teaser is zplus_registration_content and toggles('zplus_badge_gray') -%}
                                        {{- lama.use_svg_icon('zplus', 'zplus-logo zplus-logo-register zplus-logo--s svg-symbol--hide-ie', view.package, a11y=False) -}}
                                    {%- endif -%}
                                {%- endblock -%}
                                {%- if teaser.serie or teaser.blog -%}<span>{# needed for flexbox #}{%- endif -%}
                                {%- block teaser_journalistic_format -%}
                                    {%- if teaser.serie -%}
                                        <span class="series-label">{{ teaser.serie.serienname }}</span>
                                    {%- elif teaser.blog -%}
                                        <span class="blog-label">{{ teaser.blog.name }}</span>
                                    {%- endif -%}
                                {%- endblock teaser_journalistic_format -%}
                                {#- There must be no whitespace between kicker and : (for Google(News) representation) -#}
                                <span>{{ teaser.teaserSupertitle or teaser.supertitle }}</span>{%- if teaser.serie or teaser.blog -%}</span>{# needed for flexbox #}{%- endif -%}</span><span class="visually-hidden">: </span>
                        {%- endif -%}
                    {%- endblock -%}
                    {% block teaser_title %}
                        <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
                    {% endblock %}
                </a>
                {% endblock teaser_link %}
            </h2>
        {% endblock teaser_heading %}

        {% block teaser_media_position_after_title %}{% endblock %}

        {% block teaser_container %}
            {% block teaser_text %}
                <p class="{{ self.layout() }}__text">{{ teaser.teaserText }}</p>
            {% endblock teaser_text %}
            {% block teaser_metadata_default %}
            <div class="{{ self.layout() }}__metadata">
                {% block teaser_byline %}
                    {% set byline = teaser | get_byline %}
                    {% if byline | length %}
                    <span class="{{ self.layout() }}__byline">
                        {%- include 'zeit.web.core:templates/inc/meta/byline.html' -%}
                    </span>
                    {% endif %}
                {% endblock teaser_byline %}
                {% block teaser_datetime %}
                    {% if not view.is_advertorial %}
                        {{ cp.include_teaser_datetime(teaser, self.layout(), area.kind) }}
                    {% endif %}
                {% endblock teaser_datetime %}
                {% block teaser_commentcount %}
                    {% if teaser is not zplus_abo_content %}
                        {% set comments = view.comment_counts[teaser.uniqueId] %}
                        {% if comments and teaser.commentSectionEnable %}
                            {% set comments_string = comments | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') %}
                            <a class="{{ self.layout() }}__commentcount js-update-commentcount" href="{{ teaser | create_url }}#comments" data-ct-label="comments" title="Kommentare anzeigen">{{ comments_string }}</a>
                        {% endif %}
                    {% endif %}
                {% endblock teaser_commentcount %}
            </div>
            {% endblock teaser_metadata_default %}
        {% endblock %}
    </div>

    {% endblock teaser_allcontent %}

</article>
{% endblock %}
