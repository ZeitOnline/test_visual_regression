{%- extends "{0}:templates/inc/teaser/default.tpl".format(view.package) -%}

{% block layout %}volume-heading-teaser{% endblock %}


{% block teaser_journalistic_format %}
	{%- if teaser.serie %}
		{%- if teaser.serie.column %}
		   <span class="{{ self.layout() }}__series-label">{{ teaser.serie.serienname }}</span>
		{%- else %}
			<span class="{{ self.layout() }}__series-label">Serie: {{ teaser.serie.serienname }}</span>
		{%- endif %}
	{%- elif teaser.blog %}
		<span class="{{ self.layout() }}__series-label">Blog: {{ teaser.blog.name }}</span>
	{%- endif %}
{% endblock teaser_journalistic_format %}

{% block teaser_container %}{% endblock %}
