{# kind of ill. give google always a "dateModified", but don't let it be the :last-child of the parent DOM container #}
{% if not view.last_modified_label -%}
	<time itemprop="dateModified" datetime="{{ view.date_last_modified | format_date('iso8601') }}" class="metadata__date"></time>
{% endif -%}

<time itemprop="datePublished" datetime="{{ view.date_first_released | format_date('iso8601') }}" class="metadata__date">
	{{- view.date_first_released | format_date(view.show_date_format) -}}
</time>

{% if view.last_modified_label -%}
	<time itemprop="dateModified" datetime="{{ view.date_last_modified | format_date('iso8601') }}" class="metadata__date">
		{{- view.last_modified_label -}}
	</time>
{% endif -%}

{% if view.source_label -%}
	<span class="metadata__source">
		{%- if view.source_url -%}
			<a href="{{ view.source_url }}">{{ view.unobfuscated_source or view.source_label }}</a>
		{%- else -%}
			{{ view.unobfuscated_source or view.source_label }}
		{%- endif -%}
	</span>
{% endif -%}