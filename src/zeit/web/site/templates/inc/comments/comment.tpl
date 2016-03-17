{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<article id="cid-{{ comment.cid }}" class="comment
	{%- if not view.comments.sort in ('promoted', 'recommended') %}
		{%- if comment.is_reply %} comment--indented{% else %} js-comment-toplevel{% endif %}
	{%- endif %}
	{%- if comment.is_author %} comment--author{% endif %}
	{%- if comment.is_promoted %} comment--promoted{% endif %}
	{%- if comment.recommendations %} comment--recommended{% endif %}
	{%- if comment.img_url %} comment--avatar{% endif %}">
	<div class="comment__container">
		<div class="comment-meta">
			{% if comment.img_url %}
			<div class="comment-meta__avatar">
				<img alt="Avatarbild von {{ comment.name }}" src="{{ comment.img_url }}">
			</div>
			{% endif %}
			<div class="comment-meta__name">
				{% if comment.is_author or comment.is_freelancer %}
				<span title="{{ comment.role }}" class="comment-meta__badge comment-meta__badge--author">
					{{ lama.use_svg_icon('promoted', 'comment-meta__icon comment-meta__icon--author', request) }}
				</span>
				{% endif %}
				<a href="{{ comment.userprofile_url }}">{{ comment.name }}</a>
			</div>
			<a  class="comment-meta__date" href="{{ '{0}?cid={1}#cid-{1}'.format(view.content_url, comment.cid) }}">
				#{{ comment.shown_num }} &nbsp;—&nbsp; {{ comment.created | format_comment_date }}
			</a>

			<div class="comment-meta__badge comment-meta__badge--recommended" title="Leserempfehlungen"{% if not comment.recommendations %} style="display:none"{% endif %}>
				{{ lama.use_svg_icon('recommended', 'comment-meta__icon comment-meta__icon--recommended', request) }}
				<span class="js-comment-recommendations">{{ comment.recommendations }}</span>
			</div>

			{% if comment.is_promoted %}
				<div class="comment-meta__badge comment-meta__badge--promoted">
					{{ lama.use_svg_icon('promoted', 'comment-meta__icon comment-meta__icon--promoted', request) }}
					Redaktionsempfehlung
				</div>
			{% endif %}
		</div>
		<div class="comment__body">
			{{ comment.text | safe }}
		</div>
		<div class="comment__reactions">
			{% if comment.is_reply -%}
				{% set origin = view.comments.index[comment.in_reply | int] | d(None) -%}
				{% if origin -%}
					<a class="comment__origin js-jump-to-comment" href="{{ '{0}?cid={1}#cid-{1}'.format(view.content_url, comment.in_reply) }}">
						Antwort auf <strong>#{{ origin.shown_num }}</strong> von <strong>{{ origin.name }}</strong>
					</a>
				{%- endif %}
			{%- endif %}

			{% if view.comments_allowed -%}
			<a class="comment__reaction js-reply-to-comment" data-cid="{{ comment.cid }}" href="{{ view.request | append_get_params(url=view.content_url, action='comment', pid=comment.cid) }}#comment-form" title="Antworten">
				{{ lama.use_svg_icon('comment-reply', 'comment__icon comment__icon-reply', request) }}
				<span class="comment__action">Antworten</span>
			</a>
			{% endif -%}
			<a class="comment__reaction js-report-comment" data-cid="{{ comment.cid }}" href="{{ view.request | append_get_params(url=view.content_url, action='report', pid=comment.cid) }}#report-comment-form" title="Melden">
				{{ lama.use_svg_icon('comment-report', 'comment__icon comment__icon-report', request) }}
				<span class="comment__action">Melden</span>
			</a>
			<a class="comment__reaction js-recommend-comment"
			   data-cid="{{ comment.cid }}"
			   data-fans="{{ comment.fans }}"
			   data-uid="{{ comment.uid }}"
			   href="{{ view.request | append_get_params(url=view.content_url, action='recommend', pid=comment.cid) }}#cid-{{ comment.cid }}"
			   title="Empfehlen">
				{{ lama.use_svg_icon('comment-recommend', 'comment__icon comment__icon-recommend', request) }}
				<span class="comment__action">Empfehlen</span>
			</a>
		</div>
	</div>
</article>
