ckan.module('ioos_theme_hier_expand', function($) {
    return {
        initialize: function() {
        var toggler = document.getElementsByClassName("tree-caret");
        var i;

        for (i = 0; i < toggler.length; i++) {
          toggler[i].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("tree-active");
            this.classList.toggle("tree-caret-down");
            });
         }
       }
   }
});
