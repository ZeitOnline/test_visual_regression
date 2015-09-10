<div class="storystream-summary">
    <p  itemprop="description">{{ view.context.subtitle }}</p>
    <p itemscope itemtype="http://schema.org/Person" itemprop="author">
        {% set byline = view.context | get_byline %}
        {% include 'zeit.web.site:templates/inc/meta/byline.tpl' %}
    </p>
</div>
