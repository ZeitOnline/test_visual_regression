{% macro para(html, class) -%}
    <p class="is-constrained is-centered">
        {{ html | safe}}
    </p>
{%- endmacro %}

{% macro subpage_chapter(number, subtitle, class) -%}
    {% if subtitle %}
        <div class="{{ class }}">
            <span>Kapitel {{ number }}</span>
            <span>&mdash; {{ subtitle }} &mdash;</span>
            <span></span>
        </div>
    {% endif %}
{%- endmacro %}

{% macro breadcrumbs(crumbs) -%}
    <div class="breadcrumbs-wrap">
        <div class="breadcrumbs" id="js-breadcrumbs">
            <div class="breadcrumbs__trigger" id="js-breadcrumbs__trigger" data-alternate="Schlie&szlig;en">Wo bin ich?</div>
            <div class="breadcrumbs__list">
                <div class="breadcrumbs__list__item" itemprop="breadcrumb">
                    {% for crumb in crumbs %}
                        <a href="{{crumb.link}}">{{crumb.text}}</a>
                        {% if not loop.last %}
                          &rsaquo;
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
{%- endmacro %}

{% macro subpage_index(index, subtitle, number, index_class, active_class) -%}
    {% if subtitle %}
        <div class="{{ index_class }}">
        {% for chapter in index %}
            {% if loop.index == number %}
                <span class="{{ active_class }}">{{ chapter }}</span>
            {% else %}
                <span><a href="#kapitel{{ loop.index }}">{{ chapter }}</a></span>
            {% endif %}
        {% endfor %}
    </div>
    {% endif %}
{%- endmacro %}

{% macro subpage_head(number, subtitle, class) -%}
    {% if subtitle %}
        <div class="{{ class }}">
            <a name="kapitel{{ number }}"></a>
            {{ number }} &mdash; {{ subtitle }}
        </div>
    {% endif %}
{%- endmacro %}

{% macro author_date(date, source) -%}
    <span class="article__meta__source">Aus {{ source }}</span><span class="article__meta__date">{{ date }}</span>
{%- endmacro %}

{% macro intertitle(intertitle) -%}
    <h3 class="article__subheading is-constrained is-centered">
        {{ intertitle }}
    </h3>
{%- endmacro %}

{% macro citation(obj) -%}
    <blockquote class="
        {% if obj.layout == 'wide' %}
            quote--wide
        {% else %}
            quote
        {% endif %}
    ">
        <span class="quote__text">{{ obj.text }}</span>
        {% if obj.attribution %}
            {% if obj.url %}
                <span class="quote__author">
                    <a href="{{ obj.url }}">
                        {{ obj.attribution }}
                    </a>
                </span>
            {% else %}
                <span class="quote__author">{{ obj.attribution }}</span>
            {% endif %}
        {% endif %}
    </blockquote>
{%- endmacro %}

{% macro advertising(ad) -%}
    {% if ad.type == 'rectangle' %}
        <script data-name="ad__rectangle">
            (function() {
                if (window.ad_slots.rec.active_class!= null && window.location.hash === '#ads') {
                    document.write('<div class="' + window.ad_slots.rec.active_class + '">' +window.ad_slots.rec.active_text+ '</div>');
                }
            }).call(this);
        </script>
    {% endif %}
{%- endmacro %}

{% macro img(obj) -%}
    <figure class="
        {% if obj.layout == 'large' %}
            figure-full-width
        {% elif obj.layout == 'zmo_header' %}
            article__main-image figure-full-width
        {% elif obj.layout == 'medium' %}
             {% if obj.align == 'left' %}
                figure-horizontal
            {% elif obj.align == 'right' %}
                figure-horizontal--right
            {% else %}
                figure is-constrained is-centered
            {% endif %}
        {% elif obj.layout == 'small' %}
            {% if obj.align == 'right' %}
                figure-stamp--right
            {% else %}
                figure-stamp
            {% endif %}
        {% endif %}
        ">
            <img class="figure__media" src="{{obj.src | default('http://placehold.it/160x90', true)}}">
            <figcaption class="figure__caption">
                {{obj.caption}}
                {{obj.copyright}}
            </figcaption>
    </figure>
{%- endmacro %}

{% macro head_image_longform(obj) -%}
    <div class="article__main-image--longform" style="background-image: url({{obj.src | default('http://placehold.it/160x90', true)}})";>{{obj.caption}}{{obj.copyright}}
    </div>
{%- endmacro %}

{% macro meta_author(author) -%}
    {% if author -%}
        {{ author.prefix }}{{ authorlink(author) }}{{ author.suffix }}
    {%- endif %}
{%- endmacro %}

{% macro authorlink(author, class="article__meta__author") -%}
    {% if author.href -%}
        <a href="{{author.href|translate_url}}" class="{{class}} meta-link">{{author.name}}</a>
    {%- else -%}
        <span class="{{class}}">{{author.name}}</span>
    {%- endif %}
{%- endmacro %}

{% macro video(obj) -%}
    
    {% if obj.id -%}

        <figure class="
        {% if obj.layout == 'small' %}
            figure-stamp
        {% else %}
            figure is-constrained is-centered
        {% endif %}">

            <img class="figure__media" src="{{obj.video_still| default('http://placehold.it/160x90', true)}}">

            <!-- <object id="myExperience{{obj.id}}" class="BrightcoveExperience">
                <param name="htmlFallback" value="true" /> 
                <param name="bgcolor" value="#FFFFFF" />
                <param name="width" value="580" />
                <param name="height" value="327" />
                <param name="playerID" value="71289488001" />
                <param name="playerKey" value="AQ~~,AAAABDk7jCk~,Hc7JUgOccNp4D5O9OupA8T0ybhDjWLSQ" />
                <param name="isVid" value="true" />
                <param name="isUI" value="true" />
                <param name="dynamicStreaming" value="true" />
                <param name="@videoPlayer" value="{{obj.id}}" />
                <param name="includeAPI" value="false" />
                <param name="autoStart" value="true" /> 
            </object> -->

            <script type="text/javascript">
                brightcove.createExperiences();
            </script>

            <figcaption class="figure__caption">
                {{obj.subtitle}}  
            </figcaption>

        </figure>

    {%- endif %}

{%- endmacro %}
