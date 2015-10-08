{% if image and not is_image_expired(image) %}
{# TRASHME Rather crude bitblt/zci image api switch #}
{% set source = (request.image_host + image.path) if image is variant else image | default_image_url %}
{% set fallback_source = (request.image_host + image.fallback_path) if image is variant else source %}

{# TODO: check if Verlagsangebot usw. Oder check if Copyright dransteht. #}
{# TODO: dont use inline styling for display:none #}
{% if True %}
    {% set copyright_itemscope = 'itemscope itemtype="http://schema.org/Photograph"' | safe %}
    {% set copyright_item = image.copyright[0] %}
    {% if copyright_item is mapping %}
        {% set copyright_item_name, copyright_item_url = copyright_item %}
        {#% set copyright_item_name = copyright_item[0] or None %#}
        {#% set copyright_item_url = copyright_item[1] or None %#}
    {% endif %}
{% endif %}

<figure class="{% block mediablock %}{{ module_layout }}__media{% endblock %} {{ media_block_additional_class | hide_none }} scaled-image" {{ copyright_itemscope | hide_none}}>
    <!--[if gt IE 8]><!-->
    <noscript data-src="{{ fallback_source }}">
    <!--<![endif]-->
        <div class="{% block mediablock_helper %}{{ module_layout }}__media-container{% endblock %} {{ media_container_additional_class or '' }}">
            {% block mediablock_wrapper %}
            <img class="{% block mediablock_item %}{{ module_layout }}__media-item{% endblock %}" alt="{{ image.attr_title | hide_none }}" src="{{ fallback_source }}" data-src="{{ source }}" data-ratio="{{ image.ratio | hide_none }}" data-variant="{{ image.image_pattern | hide_none }}"{% if image.itemprop %} itemprop="{{ image.itemprop }}"{% endif %} {% block mediablock_additional_data_attributes %}{% endblock %}>
            {% endblock %}
            {{ media_container_after | hide_none }}
            {% if copyright_item %}
                <span itemprop="copyrightHolder" style="display:none">{{ copyright_item }}</span>
            {% endif %}
        </div>
    <!--[if gt IE 8]><!-->
    </noscript>
    <!--<![endif]-->
</figure>

{% if copyright_item %}
    <pre style="background:#c0ff33;">
        DEBUGtpuppe: {{ copyright_item }} | {{ copyright_item_name }} | {{ copyright_item_url }}
        {% for el in copyright_item %}
            - {{ el }}
        {% endfor %}
    </pre>
{% endif %}

{% endif %}
