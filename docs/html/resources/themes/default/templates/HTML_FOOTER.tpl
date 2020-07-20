            <!-- FOOTER :: START -->
            <div class="uk-flex uk-flex-center uk-flex-wrap">
<!--
                <div class="uk-card uk-card-body">
                    <span class="uk-text-meta">Last update on %s</span>
                </div>
-->
            </div>
            <!-- FOOTER :: END -->
        </div>
    </div>
    <!-- CONTENTS (Document) :: END -->
<script>
<!-- Necessary javascript for filtering results -->
<!-- Hack found in: https://codepen.io/acidrums4/pen/GBpYbO -->
var input = document.getElementById('text_filter');
var filter = document.getElementById('filter');

input.addEventListener( 'keyup', function(event)
{
    if ( input.value == "" )
    {
        filter.setAttribute( 'uk-filter-control', '' );
    }

    else
    {
        filter.setAttribute( 'uk-filter-control', 'filter:[data-title*=\'' + input.value + '\'i]' );
    }

    filter.click();
});
</script>
<script>
function copyToClipboard() {
  var copyText = document.getElementById("source-code");
  copyText.select();
  copyText.setSelectionRange(0, 99999)
  document.execCommand("copy");
  alert("Text copied to clipboard");
}
</script>
<!-- GRID LAYOUT :: END -->
</body>
</html>
