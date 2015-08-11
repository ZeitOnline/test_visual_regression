{% if image %}
{# TRASHME Rather crude bitblt/zci image api switch #}
{% set source = view.request.route_url('home') + image.path if image is variant else image | default_image_url %}

<figure class="{% block mediablock %}{{ module_layout }}__media{% endblock %} scaled-image">
    <!--[if gt IE 8]><!-->
    <noscript data-src="{{ source }}">
    <!--<![endif]-->
        <div class="{% block mediablock_helper %}{{ module_layout }}__media-container{% endblock %}">
            {% block mediablock_wrapper %}
            <img class="{% block mediablock_item %}{{ module_layout }}__media-item{% endblock %}" alt="{{ image.attr_title | hide_none }}" src="{{ source }}" data-ratio="{{ image.ratio | hide_none }}" data-variant="{{ image.image_pattern | hide_none }}" {% block mediablock_additional_data_attributes %}{% endblock %}>
            {% endblock %}
        </div>
    <!--[if gt IE 8]><!-->
    </noscript>
    <!--<![endif]-->
</figure>
{% endif %}
