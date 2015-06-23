{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama_core %}
{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% if area is undefined %}
{% set area = view %}
{% endif %}

{#
TODO:
- set region.kind for the cp-region modifier
- get right image, create dummy images for the dummy galleries
- JS
- Gallery Icon
- Button with Icon
#}

{% block before_module_list %}

  <div class="centerpage-ressort-heading">
    {# TODO: This could be a headline or something? #}
    <div class="centerpage-ressort-heading__title">Fotostrecken</div>
    {# TODO: probably we have a URL generator or something ... ? #}
    <a href="/foto/index" class="centerpage-ressort-heading__readmore-link">
      <span class="centerpage-ressort-heading__readmore-linktext">Alle Fotostrecken</span>
    </a>
  </div>

  {# TODO: is this the right way to implement a wrapper? (1/2) #}
  <div class="zon-gallery-wrapper">

{% endblock %}


{% block after_module_list %}

  {# TODO: is this the right way to implement a wrapper? (2/2) #}
  </div>

  <button type="button" class="button zon-gallery__shuffle-button" id="shuffle-gallery" onclick="shuffleGallery()">
    {{ lama_core.use_svg_icon('shuffle', 'zon-gallery__shuffle-icon', request) }}Andere laden
  </button>

  <script type="text/javascript">
  {# XXX This script is just meant to be a proof of concept. Please rewrite to your liking. #}
  function shuffleGallery() {
      var xhr = new XMLHttpRequest();
      xhr.onreadystatechange = function() {
          if (xhr.readyState == 4) {
              jQuery('.cp-area--gallery').first().parent().get(0).innerHTML = xhr.responseText;
          }
      }
      {# The random segment in the url below is supposed to generate ten (somewhat)
         different versions of this area that will still be varnish-cacheable. #}
      xhr.open("GET", "{{ view.request.path.rstrip('/') }}/area/"
                    + Math.floor(Math.random() * 10)
                    + "/{{ area.uniqueId.rsplit('/', 1)[-1] }}", true);
      xhr.send(null);
  }
  </script>
{% endblock %}
