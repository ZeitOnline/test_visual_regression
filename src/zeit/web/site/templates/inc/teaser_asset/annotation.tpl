{#
    Variable teaser asset that consists of an icon and a label, both optional.

    Context attributes
    class: Overridable base CSS class to use as a BEM-style block ID
    modifier: Arbitrary string to use as a BEM-style modifier
    icon: Compass icon class postfix
    label: Label to show in the annotation
#}

<figure class="{{ class | default('annotation') | with_mods(modifier) }}">
    {% if icon %}
        <span class="{{ (class | default('annotation') + '__icon') | with_mods(modifier) }} icon-{{ icon }}">
        </span>
    {% endif %}
    {% if label %}
        <span class="{{ (class | default('annotation') + '__label') | with_mods(modifier) }}">
            {{ label }}
        </span>
    {% endif %}
</figure>
