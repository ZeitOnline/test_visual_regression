{% macro no_block(obj) %}{% endmacro %}

{% macro citation(obj) -%}
	<aside>
	  {{ obj.text }}
	  <cite>{{ obj.attribution }}</cite>
	</aside>
{%- endmacro %}

{% macro intertitle(intertitle) -%}
    <h2>
        {{ intertitle | striptags }}
    </h2>
{%- endmacro %}

{% macro orderedlist(html) -%}
    <ol>
        {{ html | safe }}
    </ol>
{%- endmacro %}

{% macro paragraph(html) -%}
    <p>
        {{ html | safe }}
    </p>
{%- endmacro %}

{% macro unorderedlist(html) -%}
    <ul>
        {{ html | safe }}
    </ul>
{%- endmacro %}
