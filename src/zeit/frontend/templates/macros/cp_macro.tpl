{% macro lead_full(type) -%}
    <div class="cp__lead-full__wrap">
    	{% if type == 'video' %}
    		{{ lead_full_video() }}
    	{% elif type == 'image' %}
    		{{ lead_full_image() }}
    	{% endif %}
		{{ lead_full_title() }}
	</div>
{%- endmacro %}

<!-- TODO: remove test data (as)-->
{% macro lead_full_video() -%}	
	<div data-backgroundvideo="1953013471001" class="cp__lead-full">
        <video preload="auto" autoplay="true" loop="loop" muted="muted" volume="0" poster="http://brightcove.vo.llnwd.net/d21/unsecured/media/18140073001/201401/3097/18140073001_3094729885001_7x.jpg">
             <source src="http://brightcove.vo.llnwd.net/pd15/media/18140073001/201401/3809/18140073001_3094832002001_Aurora-Borealis--Northern-Lights--Time-lapses-in-Norway-Polarlichter-Der-Himmel-brennt.mp4" type="video/mp4">
              <source src="http://opendata.zeit.de/zmo-videos/1953013471001.webm" type="video/webm">
        </video>
        <img class="video--fallback" src="http://brightcove.vo.llnwd.net/d21/unsecured/media/18140073001/201401/3097/18140073001_3094729885001_7x.jpg">
    </div>
{%- endmacro %}

<!-- TODO: remove test data, switch to responsive (as)-->
{% macro lead_full_image() -%}	
	<div class="cp__lead-full">
        <img src="http://images.zeit.de/wissen/geschichte/2013-07/s79-volkstanz/s79-volkstanz-540x304.jpg">
  </div>
{%- endmacro %}

<!-- TODO: remove test data (as)-->
{% macro lead_full_title(html, class) -%}
	<header class="cp__lead-full__title__wrap">
  		<h1 class="cp__lead__title">
      		 Sie werden dich jagen!
  		</h1>
        <span class="cp__lead__subtitle">
      	Krankheit, Krisen und die Affäre um den DDR-Spion Günter Guillaume: Brandts überraschender Rücktritt im Mai 1974 war der letzte Akt einer dramatischen Kanzlerschaft. 
      	</span>
  	</header>
{%- endmacro %}