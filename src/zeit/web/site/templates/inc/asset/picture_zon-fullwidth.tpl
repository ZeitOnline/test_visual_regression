{#  Get am image with its default (Dektop) Ratio, which is configured in xml for this module type.
    It is "cinema" for Fullwidth+Classic teasers.
    For this teaser, we want a fallback image. #}
{% set image = get_image(module, fallback=True) %}
{% set href = teaser | create_url | append_campaign_params %}

{% if image %}

    {# This teaser format uses another ratio for its image on mobile devices.
       (This has nothing to do with a different motiv for mobile images.) #}
    {% set mobile_image = get_image(module, variant_id='wide', fallback=True) %}

    {# Define image sizes (widths) we want to use for this teaser.
       Maybe we move this to a more central place later. #}
    {%- set default_and_fallback_image_size = 480 %}
    {%- set mobile_image_sizes = [360, 480, 660, 767] %}
    {%- set desktop_image_sizes = [900, 1000] %}

    <figure class="{{ module_layout }}__media" itemprop="image" itemscope itemtype="http://schema.org/ImageObject">>

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

            {# xTODO: Remify ???? #}

            {# The first matching <source> will be used, so the order matters #}
            {# If no matching <source> is found, the <img> is used. #}
            {# The <img> must appear after all <source>s #}

            {# Sizes sagen, bei welchem Breakpoint das Bild wie groß sein wird. Mit 100vw als Fallback wenn keine greift.#}
            {# "The order of items within the srcset doesn't matter" #}
            {# "The browser uses the first media condition match in sizes, so the order matters" #}
            <source media = "(min-width:768px)"
                    srcset="{% for w in desktop_image_sizes %}{{ image | get_image_path(request, width=w) }} {{ w }}w{{ ', ' if not loop.last }}{% endfor %}"
                    sizes = "(min-width:1000px) 1000px, 100vw"
                    />

            {# Das "w" nennt dem Browser die Größe des Bildes. Und nicht unseren Ratschlag, wann er es einsetzen soll. Das entscheidet er selber! #}
            <source srcset="{% for w in mobile_image_sizes %}{{ mobile_image | get_image_path(request, width=w) }} {{ w }}w{{ ', ' if not loop.last }}{% endfor %}"
                    sizes = "100vw"
                    />

            {# xTODO: Wir müssen ja noch den __desktop/mobile Suffix anhängen.
               Oder lassen wir das (Vorerst) , weil nicht genutzt in Teasern? #}

                {#

                {% set image = get_image(module, fallback=fallback_image) %}
                {% set mobile_image = get_image(module, variant_id='wide', fallback=fallback_image) %}

                Der Friedbert/Template/Server kennt hier gar kein mobile_image. Sondern wir _nennen_ es nur so im Template. Und sorgen erst über den Request mit __mobile Suffix dafür, dass der Bildserver ein anders Motiv ausgibt, falls es das gibt.

                Das `if mobile_image` ist ein schönes Beispiel für kopierten sinnlosen Code, der dann Leute verwirrt. Das macht nur Sinn in einem abstrakten Template, das nicht weiß welcher Erbe mobile_image setzt. Und wir haben es jetzt überall in konkreten Templates im Eensatz, wo mobile_image gesetzt/erzeugt wird und danach wird geprüft ob es existiert.

                Den desktop/mobil Suffix fürs Motiv müssen wir noch dranmachen. Das macht bisher das JS.

                Spielt das mobile *Motiv* denn bei Teasern überhaupt eine Rolle? Oder können wir das für die Teaser-Pictures ignorieren?

                Die Ratio kommt aus der (mobile_)image.ratio, muss aber vom Template verrechnet werden in Breite/Höhe, und dann angefordert werden. Der Bildserver macht leider nicht selber ein "cinema_800" mit korrekter Höhe.

                #}

            {# Fallback for "older" browsers is the same as for mobile, because Android 4.4 and Opera Mini cant do srcset. ... Das kann aber auch das 480er Bild kriegen. Eine Variante weniger! #}

            <img class="{{ module_layout }}__media-item"
                src="{{ mobile_image | get_image_path(request, width=default_and_fallback_image_size) }}"
                alt="{{ image.alt }}"
                />

        </picture>
        </a>

            {# Optimize: Figcaption für Teaser gänzlich anders lösen als für In-Article Bilder?? #}

        <meta itemprop="url" content="{{ image | get_image_path(request, width=default_and_fallback_image_size) }}">
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
