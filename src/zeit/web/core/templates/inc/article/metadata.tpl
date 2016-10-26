<time itemprop="datePublished" datetime="{{ view.date_last_modified | format_date('iso8601') }}" class="metadata__date
    {%- if view.obfuscated_date %} encoded-date" data-obfuscated="{{ view.obfuscated_date }}{% endif %}">
    {{- view.date_last_modified | format_date(view.show_date_format) -}}
</time>

{% if view.last_modified_label -%}
    <time itemprop="dateModified" datetime="{{ view.date_last_modified | format_date('iso8601') }}" class="metadata__date">
        {{- view.last_modified_label -}}
    </time>
{% endif -%}

{% if view.source_label and not view.zplus_label.hide_source_label -%}
	<span class="metadata__source{% if view.obfuscated_source %} encoded-date" data-obfuscated="{{ view.obfuscated_source }}{% endif %}">
		{%- if view.source_url -%}
			<a href="{{ view.source_url }}"{% if view.product_id == 'merian' %} rel="nofollow"{% endif %}>{{ view.source_label }}</a>
		{%- else -%}
			{{ view.source_label }}
		{%- endif -%}
	</span>
{% endif -%}

{% if view.comment_count and view.show_commentthread %}
	{#
		span wrapper to prevent the :after-slash from being underlined
		(which would happen if a was the child which gets a slash as :after-content)
	#}
	<span>
		{% set comments_string = view.comment_count | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') %}
		<a class="metadata__commentcount js-scroll" href="#comments" title="Kommentare anzeigen">{{ comments_string }}</a>
	</span>
{% endif %}
