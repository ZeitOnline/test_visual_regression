<script>
    var $html = document.querySelector( 'html' );
    if ( $html.classList ) {
        $html.classList.replace( 'no-js', 'js' )
    } else {
        {# IE9 does not support classList #}
        var classString = $html.getAttribute( 'class' );
        classString = classString.replace( 'no-js', 'js' );
        $html.setAttribute( 'class', classString );
    }
</script>
