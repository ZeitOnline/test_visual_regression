ZEIT CAMPUS

{% require topics = view.context | topic_links %}
    <h3>{{ topics.title }}</h3>
    {% for label, link in topics %}
        <a href="{{ link }}">{{ label }}</a>
    {% endfor %}
{% endrequire %}
