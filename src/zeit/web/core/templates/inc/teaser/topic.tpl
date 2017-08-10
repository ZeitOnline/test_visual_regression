{%- extends "{0}:templates/inc/teaser/default.tpl".format(view.package) -%}

{% block layout %}teaser-topic-item{% endblock %}

{% block teaser_journalistic_format %}
	{%- if teaser.serie %}
		{%- if teaser.serie.column %}
		   <span class="{{ '%s__series-label' | format(self.layout()) | with_mods(teaser | vertical_prefix ) }}">{{ teaser.serie.serienname }}</span>
		{%- else %}
			<span class="{{ '%s__series-label' | format(self.layout()) | with_mods(teaser | vertical_prefix ) }}">Serie: {{ teaser.serie.serienname }}</span>
		{%- endif %}
	{%- elif teaser.blog %}
		<span class="{{ '%s__series-label' | format(self.layout()) | with_mods(teaser | vertical_prefix ) }}">Blog: {{ teaser.blog.name }}</span>
	{%- endif %}
{% endblock teaser_journalistic_format %}

{% block teaser_container %}{% endblock %}
