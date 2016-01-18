<time itemprop="datePublished" content="{{ view.date_first_released | format_date('iso8601') }}" datetime="{{ view.date_first_released | format_date('iso8601') }}" class="metadata__date">
	{{- view.date_first_released | format_date(view.show_date_format) -}}
</time>

{% if view.last_modified_label -%}
	<time itemprop="dateModified" content="{{ view.date_last_modified | format_date('iso8601') }}" datetime="{{ view.date_last_modified | format_date('iso8601') }}" class="metadata__date">
		{{- view.last_modified_label -}}
	</time>
{% endif -%}

{% if view.source_label -%}
	<span class="metadata__source">
		{%- if view.source_url -%}
			<a href="{{ view.source_url }}">{{ view.unobfuscated_source | default(view.source_label) }}</a>
		{%- else -%}
			{{ view.unobfuscated_source | default(view.source_label) }}
		{%- endif -%}
	</span>
{% endif -%}
