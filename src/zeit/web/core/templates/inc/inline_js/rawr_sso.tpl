<script type="text/javascript">

{# We require window.RawConfig to always have been instantiated in <head> #}
window.RawrConfig.sso = function() {
    this.remote_auth = "{{ rawr_authentication }}";
    this.name = "ZEIT ONLINE";
    this.icon = "http://images.zeit.de/static/img/favicon.ico";
    this.loginUrl = "{{ login }}";
    this.logoutUrl = "{{ logout }}";
};

</script>
