{% if image %}
    {%- set default_width = 320 %}
    {%- set default_height = (default_width / image.ratio) | int %}
    {%- set image_width = image.fallback_width | default(default_width, True) %}
    {%- set image_height = image.fallback_height | default(default_height, True) %}
    <figure class="{% block media_block %}{{ module_layout }}__media{% endblock %} {{ media_block_additional_class }} scaled-image"
        {%- block image_additional_data_attributes %}{% endblock %}
        {%- if image_itemprop %} itemprop="{{ image_itemprop }}"{% endif %} itemscope itemtype="http://schema.org/ImageObject">
        {% block media_caption_above %}{% endblock %}
        <!--[if gt IE 8]><!-->
        <noscript data-src="{{ request.image_host + image.fallback_path }}">
        <!--<![endif]-->
            <div class="{% block media_block_helper %}{{ module_layout }}__media-container{% endblock %} {{ media_container_additional_class }}">
                {% block media_block_wrapper %}
                <img class="{% block media_block_item %}{{ module_layout }}__media-item{% endblock %}"
                     alt="{{ image.alt }}"
                     src="{{ request.image_host + image.fallback_path }}"
                     data-src="{{ request.image_host + image.path }}"
                     data-ratio="{{ image.ratio }}"
                     {% block media_block_additional_data_attributes %}
                        {% if image.mobile_ratio %}data-mobile-src="{{ request.image_host + image.path }}" data-mobile-ratio="{{ image.mobile_ratio }}"{% endif %}
                    {% endblock %}>
                {% endblock %}
                {{ media_container_after }}
            </div>
        <!--[if gt IE 8]><!-->
        </noscript>
        <!--<![endif]-->
        <meta itemprop="url" content="{{ request.image_host + image.fallback_path }}">
        <meta itemprop="width" content="{{ image_width }}">
        <meta itemprop="height" content="{{ image_height }}">
        {% block media_caption -%}
        <figcaption class="{% block media_caption_class %}figure{% endblock %}__caption {{ media_caption_additional_class }}">
            {%- block media_caption_content %}
                {%- for name, url, nofollow in image.copyrights %}
                    <span class="{{ self.media_caption_class() }}__copyright" itemprop="copyrightHolder" itemscope itemtype="http://schema.org/Person">
                        {%- if url and not omit_image_links %}<a itemprop="url"{% if nofollow %} rel="nofollow"{% endif %} href="{{ url }}" target="_blank">{% endif -%}
                        <span itemprop="name">{{ name }}</span>
                        {%- if url and not omit_image_links %}</a>{% endif -%}
                    </span>
                {%- endfor %}
            {%- endblock media_caption_content -%}
        </figcaption>
        {%- endblock media_caption -%}
    </figure>
{% endif %}
