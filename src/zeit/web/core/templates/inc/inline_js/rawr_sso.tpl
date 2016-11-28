<script type="text/javascript">

{# We require window.rawrConfig to always have been instantiated in <head> #}
window.rawrConfig = window.rawrConfig || {};
window.rawrConfig.sso = function() {
    this.remote_auth = "{{ rawr_authentication }}";
    this.name = "ZEIT ONLINE";
    this.icon = "{{ request.route_url('home') }}favicon.ico";
    this.loginUrl = "{{ login }}";
    this.registerUrl = "{{ register }}";
    this.logoutUrl = "{{ logout }}";
    this.rawrReturnUrlParameter = "url";
};

</script>
