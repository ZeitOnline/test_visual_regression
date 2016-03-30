{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
<pre style="background:#c033ff;">DEBUGtpuppe: BEGIN inc/article/comments</pre>

	{#
	<pre>
	SHOW: {{ view.comment_area.show }}
	SHOW_COMMENT_FORM: {{ view.comment_area.show_comment_form }}
	SHOW_COMMENTS: {{ view.comment_area.show_comments }}
	NO_COMMENTS: {{ view.comment_area.show_comments }}
	MESSAGE: {{ view.comment_area.message }}
	NOTE: {{ view.comment_area.note }}
	USER_BLOCKED: {{ view.comment_area.user_blocked }}
	</pre>
	#}
{% if view.show_commentthread %}
{% include "zeit.web.core:templates/inc/comments/premoderation.tpl" %}
<section class="comment-section" id="comments">
	{% set query = '?' + request.query_string if request.query_string else '' %}
	{% if toggles('comment_thread_via_esi') %}
		{{ lama.insert_esi('{}/comment-thread{}'.format(view.content_url, query), 'Ein technischer Fehler ist aufgetreten. Der Kommentarbereich konnte nicht geladen werden. Bitte entschuldigen Sie diese Störung.') }}
	{% else %}
		{% include "zeit.web.core:templates/inc/comments/thread.html" %}
	{% endif %}

<pre style="background:#33c0ff;">DEBUGtpuppe: thread ----- form</pre>

	{% if view.request.GET.action == 'report' %}
        <pre style="background:#33ffc0;">A</pre>
		{% set esi_source = '{}/report-form?pid={}'.format(view.content_url, view.request.GET.pid)  %}
	{% else %}
		{% if view.request.GET.error %}
            <pre style="background:#33ffc0;">B1</pre>
			{% set esi_source = '{}/comment-form?error={}'.format(view.content_url, view.request.GET.error) %}
		{% else %}
            <pre style="background:#33ffc0;">B2</pre>
			{% set esi_source = '{}/comment-form?pid={}'.format(view.content_url, view.request.GET.pid) %}
		{% endif %}
	{% endif %}
    <pre style="background:#c0ff33;">ESI ({{ esi_source }}) before</pre>
	{{ lama.insert_esi(esi_source, 'Kommentarformular konnte nicht geladen werden') }}
    <pre style="background:#c0ff33;">ESI ({{ esi_source }}) after</pre>
	<script type="text/template" id="js-report-success-template">
		<div class="comment-form__response--success">
			Danke! Ihre Meldung wird an die Redaktion weitergeleitet.
		</div>
	</script>
</section>
{% endif %}

<pre style="background:#c033ff;">DEBUGtpuppe: END inc/article/comments</pre>
