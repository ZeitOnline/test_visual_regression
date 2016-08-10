{% block teaser %}
{% endblock %}

{% block teaser_kicker %}
    {{ lama.use_svg_icon('zplus', self.layout() + '__kicker-logo--zplus svg-symbol--hide-ie', view.package, a11y=False) }}
{% endblock %}
