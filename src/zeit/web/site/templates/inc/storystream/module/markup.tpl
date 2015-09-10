{% set blockname = 'storystream-markup' %}
<article class="{{ blockname }}">
    <h2 class="{{ blockname }}__title">{{ module.title | hide_none }}</h2>
    <div class="{{ blockname }}__text">
        {{ module.text | hide_none | safe }}
    </div>
</article>
