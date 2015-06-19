{# %- extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" -% #}

{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}


<article class="gallery-teaser" data-unique-id="{{ teaser.uniqueId }}">
  <pre>One Module</pre>
</article>



{#% block layout %}teaser-small{% endblock %#}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}_zon-thumbnail.tpl".format(teaser | auto_select_asset | block_type)
        ignore missing with context %}
{% endblock %}


{# % block teaser_metadata_default %}
<small class="{{ self.layout() }}__counter">
    {{ teaser.keys() | list | length | pluralize('Keine Fotos', 'Ein Foto', '{} Fotos') }}
</small>
{% endblock % #}
