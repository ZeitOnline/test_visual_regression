{#% extends "zeit.web.site:templates/inc/area/default.html" %#}

{% if area is undefined %}
{% set area = view %}
{% endif %}

{% block before_module_list %}
  <div class="centerpage-ressort-heading">
    {# TODO: This could be a headline or something? #}
    <div class="centerpage-ressort-heading__title">Fotostrecken</div>
    {# TODO: probably we have a URL generator or something ... ? #}
    <a href="/foto/index" class="centerpage-ressort-heading__readmore-link">
      <span class="centerpage-ressort-heading__readmore-linktext">Alle Fotostrecken</span>
    </a>
  </div>
{% endblock %}


{% block after_module_list %}
<button type="button" id="shuffle-gallery" onclick="shuffleGallery()">
    Andere laden
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


<pre>Gallery.tpl ohne Block. Und ohne Extends.</pre>
