{% if image and not image is expired %}
    {%- set width = 820 %}
    {%- set height = 460 %}
    {%- if image.ratio %}
        {%- set height = (width / image.ratio) | int %}
    {%- endif %}

    {# TRASHME Rather crude bitblt/zci image api switch #}
    {%- if image is variant %}
        {%- set source = request.image_host + image.path | replace(' ', '%20') %}
        {%- set fallback_source = request.image_host + image.fallback_path | replace(' ', '%20') -%}
        {%- set url = "%s__%sx%s" | format(source, width, height) %}
    {%- else %}
        {%- set source = image | default_image_url | replace(' ', '%20') -%}
        {%- set fallback_source = source -%}
        {%- set url = source %}
    {%- endif %}

    <figure class="{% block media_block %}{{ module_layout }}__media{% endblock %} {{ media_block_additional_class }} scaled-image"
        {%- if image_itemprop %} itemprop="{{ image_itemprop }}"{% endif %} itemscope itemtype="http://schema.org/ImageObject">
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
        <meta itemprop="url" content="{{ url }}">
        <meta itemprop="width" content="{{ width }}">
        <meta itemprop="height" content="{{ height }}">
        {% block media_caption -%}
        <figcaption class="{% block media_caption_class %}figure{% endblock %}__caption {{ media_caption_additional_class }}">
            {%- block media_caption_content %}
                {%- for name, url, nofollow in image.copyright %}
                    {%- if name | trim | length > 1 %}
                        <span class="{{ self.media_caption_class() }}__copyright" itemprop="copyrightHolder" itemscope itemtype="http://schema.org/Person">
                            {%- if url and not omit_image_links %}<a itemprop="url"{% if nofollow %} rel="nofollow"{% endif %} href="{{ url }}" target="_blank">{% endif -%}
                            <span itemprop="name">{{ name | trim | replace('© ', '© ') }}</span>
                            {%- if url and not omit_image_links %}</a>{% endif -%}
                        </span>
                    {%- endif %}
                {%- endfor %}
            {%- endblock media_caption_content -%}
        </figcaption>
        {%- endblock media_caption -%}
    </figure>
{% endif %}
