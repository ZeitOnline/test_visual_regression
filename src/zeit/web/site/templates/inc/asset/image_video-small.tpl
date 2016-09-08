{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = 'video-thumbnail' %}
{% block media_block %}{{ module_layout }} {{ module_layout }}--small{% endblock %}

{% block media_caption -%}
    {% if teaser.video_still_copyright and teaser.video_still_copyright | trim | length > 7 %}
        <figcaption class="figure__caption figure__caption--hidden">
            <span class="video-figure__copyright" itemprop="copyrightHolder" itemscope itemtype="http://schema.org/Person">
                <span itemprop="name">{{ teaser.video_still_copyright | trim | replace('© Foto: ', '© Foto: ') }}</span>
            </span>
        </figcaption>
        {% endif %}
{%- endblock media_caption -%}
