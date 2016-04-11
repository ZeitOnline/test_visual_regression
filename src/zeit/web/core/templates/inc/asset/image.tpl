{% if image and not is_image_expired(image) %}
    {# TRASHME Rather crude bitblt/zci image api switch #}
    {% set source = (request.image_host + image.path) if image is variant else image | default_image_url %}
    {% set fallback_source = (request.image_host + image.fallback_path) if image is variant else source %}

    <figure class="{% block media_block %}{{ module_layout }}__media{% endblock %} {{ media_block_additional_class }} scaled-image"
        {%- if image.itemprop %} itemprop="{{ image.itemprop }}"{% endif %} itemscope itemtype="http://schema.org/ImageObject">
        <!--[if gt IE 8]><!-->
        <noscript data-src="{{ fallback_source }}">
        <!--<![endif]-->
            <div class="{% block media_block_helper %}{{ module_layout }}__media-container{% endblock %} {{ media_container_additional_class }}">
                {% block media_block_wrapper %}
                <img class="{% block media_block_item %}{{ module_layout }}__media-item{% endblock %}" alt="{{ image.alt }}" src="{{ fallback_source }}" data-src="{{ source }}" data-ratio="{{ image.ratio }}" data-variant="{{ image.image_pattern }}" {% block media_block_additional_data_attributes %}{% endblock %}>
                {% endblock %}
                {{ media_container_after }}
            </div>
        <!--[if gt IE 8]><!-->
        </noscript>
        <!--<![endif]-->
        {% block media_caption -%}
        <figcaption class="figure__caption {{ media_caption_additional_class }}">
            {%- block media_caption_content %}
                {%- for name, url, nofollow in image.copyright %}
                    {%- if name | trim | length > 1 %}
                        <span class="figure__copyright" itemprop="copyrightHolder" itemscope itemtype="http://schema.org/Person">
                            {%- if url and not omit_image_links %}<a itemprop="url"{% if nofollow %} rel="nofollow"{% endif %} href="{{ url }}" target="_blank">{% endif -%}
                            <span itemprop="name">{{ name }}</span>
                            {%- if url and not omit_image_links %}</a>{% endif -%}
                        </span>
                    {%- endif %}
                {%- endfor %}
            {%- endblock media_caption_content -%}
        </figcaption>
        {%- endblock media_caption -%}
    </figure>
{% endif %}
