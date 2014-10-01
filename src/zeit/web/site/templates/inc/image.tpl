{% set image = get_teaser_image(block, teaser) %}

{% if image %}
<figure class="{% block mediablock %}{% endblock %} scaled-image">
    <!--[if gt IE 8]><!-->
    <noscript data-src="{{ image | default_image_url }}">
    <!--<![endif]-->
        <a class="{% block mediablock_link %}{% endblock %}" title="{{ image.attr_title | default('') }}" href="{{ image.href }}">
            <img class="{% block mediablock_item %}{% endblock %}" alt="{{ image.attr_title }}"  src="{{ image | default_image_url }}" data-ratio="{{ image.ratio }}">
        </a>
    <!--[if gt IE 8]><!-->
    </noscript>
    <!--<![endif]-->
</figure>
{% endif %}
