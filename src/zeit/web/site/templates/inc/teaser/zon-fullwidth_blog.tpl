{%- extends "zeit.web.site:templates/inc/teaser/zon-fullwidth.tpl" -%}

{% block teaser_modifier %}{{ self.layout()}}--blog{% endblock %}

{% block teaser_media_position_before_title %}
    {{ super() }}
    <div class="blog-format blog-format--fullwidth">
        <span class="blog-format__marker blog-format__marker--fullwidth">Blog</span>
        <span class="blog-format__name blog-format__name--fullwidth">{{ teaser.blog.name }}</span>
    </div>
{% endblock %}

{% block teaser_journalistic_format %}{% endblock %}
