{%- extends "{0}:templates/inc/teaser/default.tpl".format(view.package) -%}

{% block layout %}teaser-topic-item{% endblock %}

{% block teaser_journalistic_format %}
    {%- if teaser.blog %}
        <span class="{{ '%s__series-label' | format(self.layout()) | with_mods(teaser | branding ) }}">Blog: {{ teaser.blog.name }}</span>
    {%- else %}
        {{- super() -}}
    {%- endif %}
{% endblock teaser_journalistic_format %}

{% block teaser_container %}{% endblock %}
