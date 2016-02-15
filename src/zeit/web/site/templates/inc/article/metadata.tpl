<time itemprop="datePublished" datetime="{{ view.date_last_modified | format_date('iso8601') }}" class="metadata__date
	{%- if view.obfuscated_date %} encoded-date" data-obfuscated="{{ view.obfuscated_date }}{% endif %}">
	{{ view.date_last_modified | format_date(view.show_date_format) }}
</time>

{% if view.source_label -%}
	<span class="metadata__source{% if view.obfuscated_source %} encoded-date" data-obfuscated="{{ view.obfuscated_source }}{% endif %}">
		{%- if view.source_url -%}
			<a href="{{ view.source_url }}">{{ view.source_label }}</a>
		{%- else -%}
			{{ view.source_label }}
		{%- endif -%}
	</span>
{% endif -%}

{% if view.comments %}
	{#
		span wrapper to prevent the :after-slash from being underlined
		(which would happen if a was the child which gets a slash as :after-content)
	#}
	<span>
		{% set comments_string = view.comments.comment_count | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') %}
		<a class="metadata__commentcount js-scroll" href="#comments" title="Kommentare anzeigen">{{ comments_string }}</a>
	</span>
{% endif %}
