{% set image = get_teaser_image(module, teaser) %}

{% if image %}
<figure class="{% block mediablock %}{% endblock %} scaled-image">
    <!--[if gt IE 8]><!-->
    <noscript data-src="{{ image | default_image_url }}">
    <!--<![endif]-->
        <div class="mediablock__helper">
            <a class="{% block mediablock_link %}{% endblock %}" title="{{ image.attr_title | default('') }}" href="{{ teaser.uniqueId | translate_url }}">
                <img class="{% block mediablock_item %}{% endblock %}" alt="{{ image.attr_title }}"  src="{{ image | default_image_url }}" data-ratio="{{ image.ratio }}">
            </a>
        </div>
    <!--[if gt IE 8]><!-->
    </noscript>
    <!--<![endif]-->
</figure>
{% endif %}
