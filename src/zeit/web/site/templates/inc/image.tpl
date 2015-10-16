{% if image and not is_image_expired(image) %}
{# TRASHME Rather crude bitblt/zci image api switch #}
{% set source = (request.image_host + image.path) if image is variant else image | default_image_url %}
{% set fallback_source = (request.image_host + image.fallback_path) if image is variant else source %}


{% if view.type == 'centerpage' and image.copyright %}
    {% set copyright_itemscope = 'itemscope itemtype="http://schema.org/Photograph"' | safe %}
    {% set copyright_item = image.copyright[0] %}
    {#
    TODO: zwei Items aus nem Tuple auslesen kann doch nicht so schwer sein !!!
    Oder machen wir das lieber im Python-Code? `(name, url) = tuple`
    #}
    {% set copyright_item_values = [] %}
    {% for el in copyright_item %}
        {% if loop.index == 1 %}
            {% if copyright_item_values.append( el ) %}{% endif %}
        {% endif %}
        {% if loop.index == 2 %}
            {% if copyright_item_values.append( el ) %}{% endif %}
        {% endif %}
    {% endfor %}
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

            {% if copyright_item_values and copyright_item_values[0] %}
                <span itemprop="copyrightHolder" class="figureCopyrightHidden">
                    {% if copyright_item_values[1] %}<a itemprop="url" href="{{ copyright_item_values[1] }}"><span itemprop="name">{% endif %}
                        {{ copyright_item_values[0] }}
                    {% if copyright_item_values[1] %}</span></a>{% endif %}
                </span>
            {% endif %}

        </div>
    <!--[if gt IE 8]><!-->
    </noscript>
    <!--<![endif]-->
</figure>
{% endif %}
