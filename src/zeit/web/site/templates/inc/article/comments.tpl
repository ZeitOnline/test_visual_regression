<section class="comment-section" id="comments">
	<div class="comment-section__head">
		{% if view.comments and view.comments.comment_count %}
			<span class="comment-section__headline">
				{%- if view.comments.comment_count != 1 -%}
					{{ view.comments.comment_count }} Kommentare
				{%- else -%}
					1 Kommentar
				{%- endif -%}
			</span>
			<a href="#comment-form" class="comment-section__cta">
				Kommentieren
			</a>
		{% else %}
			<span class="comment-section__headline">
				<span class="nowrap">Noch keine Kommentare.</span>
				<span class="nowrap">Diskutieren Sie mit.</span>
			</span>
		{% endif %}
	</div>

{% if view.comments %}
	{% for comment in view.comments.comments[:20] %}
	<article class="comment{% if comment.is_reply %} comment--indented{% endif %}{% if comment.is_author %} comment--author{% endif %}" id="cid-{{ comment.cid }}">
		<div class="comment__container">
			{% if comment.img_url %}
			<img class="comment__avatar" alt="Avatarbild von {{ comment.name | e }}" src="{{ comment.img_url }}">
			{% endif %}
			<div class="comment__meta">
				{% if comment.is_author %}
				<span class="icon-comment-zon-author-badge"></span>
				{% endif %}
				<a class="comment__name" href="{{ comment.userprofile_url }}">
					{{ comment.name | e }}
				</a>
				{% if comment.recommendations %}
				{# Special-Char: &#9733; = Black Star #}
				<span class="comment__recommendations" title="{{ comment.recommendations }} Leserempfehlung{% if comment.recommendations != 1 %}en{% endif %}">
					{{ comment.recommendations }} &#9733;
				</span>
				{% endif %}
				<a  class="comment__date" href="#cid-{{ comment.cid }}">
				#{{ loop.index }} &nbsp;/&nbsp; {{ comment.timestamp | format_date_ago() }}
				</a>
			</div>
			<div class="comment__body">
				{{ comment.text | safe }}
			</div>
			<div class="comment__reactions">
				<a class="comment__reaction" href="#cid-{{ comment.cid }}" title="Antworten">
					<span class="icon-comment-reactions-reply"></span>
					<span class="comment__action">Antworten</span>
				</a>
				<a class="comment__reaction" href="#cid-{{ comment.cid }}" title="Melden">
					<span class="icon-comment-reactions-report"></span>
					<span class="comment__action">Melden</span>
				</a>
				<a class="comment__reaction" href="#cid-{{ comment.cid }}" title="Empfehlen">
					<span class="icon-comment-reactions-recommend"></span>
					<span class="comment__action">Empfehlen</span>
				</a>
			</div>
		</div>
	</article>
	{% endfor %}
{% endif %}

<esi:include src="{{ view.article_url }}/comment-form" />

</section>
