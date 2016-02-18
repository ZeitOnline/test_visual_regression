<article>
    {% set module_layout = 'teaser' %}
    {% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" ignore missing %}
    <div>
        <small>{{ teaser.supertitle }}</small>
    </div>
    <div>
        <big>{{ teaser.title }}</big>
    </div>
    <div>
        <span>{{ teaser.teaserText }}</span>
    </div>
    <br/>
</article>
