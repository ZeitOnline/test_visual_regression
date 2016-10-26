{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}volume{% endblock %}

{% block teaser %}
<pre style="background:#c0ff33;">Module: {{ module }}</pre>
<pre style="background:#c0ff33;">first_child: {{ module | first_child }}</pre>
{% endblock %}
