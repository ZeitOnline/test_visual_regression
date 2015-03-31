{% if view.source_label -%}
	<span class="metadata__source{% if view.obfuscated_source %} encoded-date" data-obfuscated="{{ view.obfuscated_source }}{% endif %}">
		{%- if view.source_url -%}
		<a href="{{ view.source_url }}">{{ view.source_label }}</a> -
		{%- else -%}
		{{ view.source_label }}
		{%- endif -%}
	</span>
{% endif -%}

<time class="metadata__date{% if view.obfuscated_date %} encoded-date" data-obfuscated="{{ view.obfuscated_date }}{% endif %}" datetime="{{ view.date_last_modified | format_date('iso8601') }}">
	{{- view.date_last_modified | format_date(view.show_date_format) -}}
</time>
