{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama_core %}
{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% if area is undefined %}
{% set area = view %}
{% endif %}

{#
TODO:
- get right image, create dummy images for the dummy galleries
- JS
#}

{% block before_module_list %}
  <div class="cp-ressort-heading">
    {# TODO: This could be a headline or something? #}
    <h6 class="cp-ressort-heading__title">Fotostrecken</h6>
    <a href="{{ view.request.route_url('home') }}foto/index" class="cp-ressort-heading__readmore-link">
      <span class="cp-ressort-heading__readmore-linktext">Alle Fotostrecken</span>
    </a>
  </div>
{% endblock %}

{% block module_list %}
  <div class="zon-gallery-group__container">
    {{ super() }}
  </div>
{% endblock %}

{% block after_module_list %}
  <button type="button" class="button zon-gallery-group__shuffle-button" id="shuffle-gallery" onclick="shuffleGallery()">
    {{ lama_core.use_svg_icon('shuffle', 'zon-gallery-group__shuffle-icon', request) }}Andere laden
  </button>

  <script type="text/javascript">
  {# XXX This script is just meant to be a proof of concept. Please rewrite to your liking. #}
  {# TODO: run imageJS after loading the new images #}
  {# TODO: put this into a requireJS module ??? #}
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
