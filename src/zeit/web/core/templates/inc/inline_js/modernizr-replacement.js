( function( ) {

    var $html = document.querySelector( 'html' );

    function replaceClass( search, replace ) {
        if ( $html.classList ) {
            $html.classList.replace( search, replace );
        } else {
            // IE9 does not support classList
            var classString = $html.getAttribute( 'class' );
            classString = classString.replace( search, replace );
            $html.setAttribute( 'class', classString );
        }
    }

    function setClass( classname ) {
        if ( $html.classList ) {
            $html.classList.add( classname );
        } else {
            // IE9 does not support classList
            var classString = $html.getAttribute( 'class' );
            classString+= ' ' + classname;
            $html.setAttribute( 'class', classString );
        }
    }

    // .(no-)js as basic
    replaceClass( 'no-js', 'js');

    // .no-flexbox is needed for our main menu, thats why we check it early
    var testElem = document.createElement('div');
    if( testElem.style.flex !== undefined &&
        testElem.style.flexFlow !== undefined &&
        testElem.style.flexBasis !== undefined )
    {
        setClass( 'flexbox' );
    } else {
        setClass( 'no-flexbox' );
    }

})( );
