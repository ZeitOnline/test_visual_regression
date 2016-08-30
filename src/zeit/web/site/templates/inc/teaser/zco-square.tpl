{%- extends "zeit.web.site:templates/inc/teaser/zon-square.tpl" -%}

{% block teaser_modifier %}{{ self.layout() }}--zco{% endblock %}

{% block kicker_logo %}
    {{ self.zplus_kicker_logo() }}
{% endblock %}

{% block teaser_container %}
    <div class="teaser-square__product">
        {{ lama.use_svg_icon('logo-zco', 'teaser-square__zco-logo', 'zeit.web.campus') }}
    </div>
{% endblock %}
