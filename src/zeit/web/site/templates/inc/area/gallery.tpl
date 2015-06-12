{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% if area is undefined %}
{% set area = view %}
{% endif %}

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
