{% if image and not is_image_expired(image) %}
{# TRASHME Rather crude bitblt/zci image api switch #}
{% set source = request.image_host + image.path if image is variant else image | default_image_url %}
{% set fallback_source = request.image_host + image.fallback_path if image is variant else source %}

<figure class="{% block mediablock %}{{ module_layout }}__media{% endblock %} {{ media_block_additional_class | hide_none }} scaled-image">
    <!--[if gt IE 8]><!-->
    <noscript data-src="{{ fallback_source }}">
    <!--<![endif]-->
        <div class="{% block mediablock_helper %}{{ module_layout }}__media-container{% endblock %} {{ media_container_additional_class | hide_none }}">
            {% block mediablock_wrapper %}
            <img class="{% block mediablock_item %}{{ module_layout }}__media-item{% endblock %}" alt="{{ image.attr_title | hide_none }}" src="{{ fallback_source }}" data-src="{{ source }}" data-ratio="{{ image.ratio | hide_none }}" data-variant="{{ image.image_pattern | hide_none }}"{% if image.itemprop %} itemprop="{{ image.itemprop }}"{% endif %} {% block mediablock_additional_data_attributes %}{% endblock %}>
            {% endblock %}
            {{ media_container_after | hide_none }}
        </div>
    <!--[if gt IE 8]><!-->
    </noscript>
    <!--<![endif]-->
</figure>
{% endif %}
