<div class="liveblog-status">
	<div class="liveblog-status__label{% if view.liveblog_is_live %} liveblog-status__label--live{% endif %}">
		Live Blog
	</div>
	<div class="liveblog-status__meta">
		<span class="liveblog-status__meta-date">
			{{ view.liveblog_last_modified | format_date('short') }}
		</span>
		<span class="liveblog-status__meta-divider"></span>
		<span class="liveblog-status__meta-updated">
		{%- if view.liveblog_is_live -%}
			{{ view.liveblog_last_modified | format_date('timedelta') }} aktualisiert
		{%- else -%}
			Liveblog abgeschlossen
		{%- endif -%}
		</span>
	</div>
</div>
