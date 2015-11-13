{% if image and not is_image_expired(image) %}
    {# TRASHME Rather crude bitblt/zci image api switch #}
    {% set source = (request.image_host + image.path) if image is variant else image | default_image_url %}
    {% set fallback_source = (request.image_host + image.fallback_path) if image is variant else source %}

    <figure class="{% block media_block %}{{ module_layout }}__media{% endblock %} {{ media_block_additional_class }} scaled-image" itemscope itemtype="http://schema.org/Photograph">
        <!--[if gt IE 8]><!-->
        <noscript data-src="{{ fallback_source }}">
        <!--<![endif]-->
            <div class="{% block media_block_helper %}{{ module_layout }}__media-container{% endblock %} {{ media_container_additional_class }}">
                {% block media_block_wrapper %}
                <img class="{% block media_block_item %}{{ module_layout }}__media-item{% endblock %}" alt="{{ image.alt }}" src="{{ fallback_source }}" data-src="{{ source }}" data-ratio="{{ image.ratio }}" data-variant="{{ image.image_pattern }}"{% if image.itemprop %} itemprop="{{ image.itemprop }}"{% endif %} {% block media_block_additional_data_attributes %}{% endblock %}>
                {% endblock %}
                {{ media_container_after }}
            </div>
        <!--[if gt IE 8]><!-->
        </noscript>
        <!--<![endif]-->
        <figcaption class="figure__caption {{ media_caption_additional_class }}">
            {% block media_caption_content %}
                {% for name, url, nofollow in image.copyright %}

                {# copyright URLs for images destroy the printkiosk teaser. That's why we suppress them. #}
                {% if module_layout == 'teaser-printkiosk' %}{% set url = None %}{% endif %}

                <span class="figure__copyright" itemprop="copyrightHolder">
                    {% if url %}<a itemprop="url"{% if nofollow %} rel="nofollow"{% endif %} href="{{ url }}" target="_blank">{% endif %}
                    {% if name | trim | length > 1 %}<span itemprop="name">{{ name }}</span>{% endif %}
                    {% if url %}</a>{% endif %}
                </span>
                {% endfor %}
            {% endblock %}
        </figcaption>
    </figure>
{% endif %}
