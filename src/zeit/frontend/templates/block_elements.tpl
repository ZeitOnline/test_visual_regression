{% macro p(html, class) -%}
    <p class="{{ class }}">
        {{ html | safe}}
    </p>
{%- endmacro %}
{% macro intertitle(intertitle) -%}
    <h2>
        {{ intertitle }}
    </h2>
{%- endmacro %}
{% macro image(obj) -%}
    <figure class="figure-stamp">
      <img class="figure__media" src="http://images.zeit.de/lebensart/mode/2013-10/teaser-vinken-interview/teaser-vinken-interview-180xVar.jpg">
      <figcaption class="figure__caption">Schätze lagern im südafrikanischen Stellenbosch in so manchem Weinkeller. Die richtige Mikrobenkultur könnte sie noch weiter veredeln.   |  © Kai Pfaffenbach/Reuters</figcaption>
    </figure>
{%- endmacro %}

