{% if image %}
<figure class="{% block mediablock %}{{ teaser_block_layout }}__media{% endblock %} scaled-image">
    <!--[if gt IE 8]><!-->
    <noscript data-src="{{ image | default_image_url }}">
    <!--<![endif]-->
        <div class="{% block mediablock_helper %}{{ teaser_block_layout }}__media-container{% endblock %}">
            {% block mediablock_wrapper %}
            <img class="{% block mediablock_item %}{{ teaser_block_layout }}__media-item{% endblock %}" alt="{{ image.attr_title }}" src="{{ image | default_image_url }}" data-ratio="{{ image.ratio }}">
            {% endblock %}
        </div>
    <!--[if gt IE 8]><!-->
    </noscript>
    <!--<![endif]-->
</figure>
{% endif %}
