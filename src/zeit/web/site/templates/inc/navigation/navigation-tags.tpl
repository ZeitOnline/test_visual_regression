{# <!-- be careful with line break: display-block alignment --> #}
<span class="main_nav__tags__label">{{ view.topiclink_title }}</span><ul>
{% for label, link in view.topiclinks %}
	<li>
		<a href='{{link}}' title='{{label}}'>{{label}}</a>
	</li>
{% endfor %}
</ul>
