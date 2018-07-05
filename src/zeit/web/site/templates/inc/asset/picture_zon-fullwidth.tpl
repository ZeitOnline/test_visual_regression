{#  Get am image with its default (Dektop) Ratio, which is configured in xml for this module type.
    It is "cinema" for Fullwidth+Classic teasers.
    For this teaser, we want a fallback image. #}
{% set image = get_image(module, fallback=True) %}

{% if image %}

    {% set href = teaser | create_url | append_campaign_params %}
    {% set image_host = request.image_host %}

    {# This teaser format uses another ratio for its image on mobile devices.
       (This has nothing to do with a different motiv for mobile images.) #}
    {% set mobile_image = get_image(module, variant_id='wide', fallback=True) %}

    {# Define image sizes (widths) we want to use for this teaser.
       Maybe we move this to a more central place later. #}
    {%- set default_and_fallback_image_size = 980 %}
    {%- set mobile_image_sizes = [360, 480, 660, 767] %}
    {%- set desktop_image_sizes = [900, 1000] %}

    <figure class="{{ module_layout }}__media" itemscope itemtype="http://schema.org/ImageObject">

        {# OPTIMIZATION: Für Teaser, bei denen sich zwischen Mobil-Desktop nicht
           die Ratio ändert, könnte man auf die harte vorgeschriebene Grenze
           (source mit Media Query) verzichten, und via srcset den Browsern den
           Bildwechsel "vorschlagen" statt erzwingen. #}

        <a class="{{ module_layout }}__media-link"
           title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}"
           href="{{ href }}"
            {%- if image.nofollow %} rel="nofollow"{% endif %}
            {%- if tracking_slug %} data-id="{{ tracking_slug }}image"{% endif %}>

        <picture class="{{ module_layout }}__media-container">

            {# The first matching <source> will be used, so the order matters #}
            {# If no matching <source> is found, the <img> is used. #}
            {# The <img> must appear after all <source>s #}

            {# Sizes sagen, bei welchem Breakpoint das Bild wie groß sein wird. Mit 100vw als Fallback wenn keine greift. #}
            {# "The order of items within the srcset doesn't matter" #}
            {# "The browser uses the first media condition match in sizes, so the order matters" #}
            <source media = "(min-width:768px)"
                    srcset="{% for w in desktop_image_sizes %}{{ image_host }}{{ image | get_image_path(w) }} {{ w }}w{{ ', ' if not loop.last }}{% endfor %}"
                    sizes = "(min-width:1000px) 1000px, 100vw"
                    />

            {# Das "w" nennt dem Browser die Größe des Bildes. Und nicht unseren Ratschlag, wann er es einsetzen soll. Das entscheidet er selber! #}
            <source srcset="{% for w in mobile_image_sizes %}{{ image_host }}{{ mobile_image | get_image_path(w) }} {{ w }}w{{ ', ' if not loop.last }}{% endfor %}"
                    sizes = "100vw"
                    />

            {# xTODO: Bei breiterem Einsatz müssen wir noch den __desktop/mobile Suffix anhängen.
               Vorerst lassen wir das, weil nicht genutzt in den Lead-Teasern, die unser Testcase
               Für responsive images sind. #}

            {# Fallback for "older" browsers is the same as for mobile, because Android 4.4 and Opera Mini cant do srcset. #}

            <img class="{{ module_layout }}__media-item"
                src="{{ image_host }}{{ image | get_image_path(default_and_fallback_image_size) }}"
                alt="{{ image.alt }}"
                />

        </picture>
        </a>

        {# OPTIMIZATION: Figcaption für Teaser gänzlich anders lösen als für In-Article Bilder?? #}

        <meta itemprop="url" content="{{ image_host }}{{ image | get_image_path(default_and_fallback_image_size) }}">
        <meta itemprop="width" content="{{ default_and_fallback_image_size }}">
        <meta itemprop="height" content="{{ (default_and_fallback_image_size / image.ratio) | int }}">

        {% block media_caption -%}
            <figcaption class="{% block media_caption_class %}figure{% endblock %}__caption figcaption--hidden">
                {%- block media_caption_content %}
                    {%- for item in image.copyrights %}
                        <span class="{{ self.media_caption_class() }}__copyright" itemprop="copyrightHolder" itemscope itemtype="http://schema.org/Person">
                            {%- if item.url and not omit_image_links %}<a itemprop="url"{% if item.nofollow %} rel="nofollow"{% endif %} href="{{ item.url }}" target="_blank">{% endif -%}
                            <span itemprop="name">{{ item.text }}</span>
                            {%- if item.url and not omit_image_links %}</a>{% endif -%}
                        </span>
                    {%- endfor %}
                {%- endblock media_caption_content -%}
            </figcaption>
        {%- endblock media_caption -%}

    </figure>
{% endif %}
