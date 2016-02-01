// CeleraOne dummy tracking client

window.cre_client = function() {
    var client = function() {
        this.params = {};
        this.addListener = function( event ) {}
        this.getParams = function() {}
        this.set_page_view = function() {}

        this.set_channel = function( value ) {
            this.params['channel'] = value;
        }
        this.set_sub_channel = function( value ) {
            this.params['sub_channel'] = value;
        }
        this.set_cms_id = function( value ) {
            this.params['cms_id'] = value;
        }
        this.set_content_id = function( value ) {
            this.params['content_id'] = value;
        }
        this.set_doc_type = function( value ) {
            this.params['doc_type'] = value;
        }
        this.set_heading = function( value ) {
            this.params['heading'] = value;
        }
        this.set_kicker = function( value ) {
            this.params['kicker'] = value;
        }
        this.set_service_id = function( value ) {
            this.params['service_id'] = value;
        }
        this.set_origin = function( value ) {
            this.params['origin'] = value;
        }
        this.request = function() {
            console.log( this.params );
        }
    };
    return new client
}();
