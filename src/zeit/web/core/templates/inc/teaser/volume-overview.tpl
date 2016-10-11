<div class="volume-teaser article__item article__item--marginalia" data-clicktracking="volumeteaser">
    {% for block in area.values()-%}
        <pre style="background-color: greenyellow">{{ block }}</pre>
        {% include "{}:templates/inc/asset/image_volumeteaser.tpl".format(view.package) ignore missing %}
    {% endfor %}
</div>
