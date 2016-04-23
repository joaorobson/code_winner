$.fn.submitWith = function(data) {
    var select;
    form = this[0];

    for (var k in data) {
        select = $(form).find('[name=%s]'.replace('%s', k))[0];
        select.value = data[k];
    }

    return $(form).submit();
};


var $styles = {

    elements: $(),

    /**
     * Apply all styles
     */
    applyAll: function() {
        this.applyFormElements();

        this.elements.each(function(idx, elem) {
           componentHandler.upgradeElement(this);
        });
    },

    /**
     * Apply material style to all form elements
     */
    applyFormElements: function() {
        // Buttons
        var buttons = $('button, input[type="button"], input[type="reset"], input[type="submit"], a.button');

        buttons.addClass('mdl-button mdl-js-button mdl-js-ripple-effect');
        buttons.filter('.primary, [raised]').addClass('mdl-shadow--4dp mdl-button--raised');
        buttons.exclude('.flat').addClass('mdl-button--raised');
        this.elements = this.elements.add(buttons);

        //// Input text
        //var inputs = $('input[type="text"], input[type="number"], input[type="email"]');
        //inputs.addClass('mdl-textfield__input');
        //this.elements = this.elements.add(inputs);
        //
        //var textarea = $('textarea');
        //textarea.addClass('mdl-textfield__input');
        //this.elements = this.elements.add(textarea);
        //
        //// Labels
        //var labels = $('label[for]');
        //labels.addClass('mdl-textfield__label');
        //this.elements = this.elements.add(labels);
    },

};




$(function() {
    // Make sortable-js understand the sync-api and sync-id attributes when
    // sorting
    $('sortable-js').on('update', function() {
        var state = this.sortable.toArray();
        var api_url = (this.attributes['sync-api'] || {}).nodeValue;
        var api_id = (this.attributes['sync-id'] || {}).nodeValue;

        if (api_url) {
            if (('' + this.__array_state) === ('' + state)) {
                return;
            }
            this.__array_state = state;
        }
        $.srvice(api_url, {owner_ref: api_id || null, order: state});
    });

    // Enable the remove button from sortable-remove classes
    $('sortable-js .sortable-remove')
        .fadeTo(1, 0.1)
        .hover(
            function() {$(this).fadeTo(0.1, 1)},
            function() {$(this).fadeTo(1, 0.1)}
        )
        .click(function () {
            var sortable = this.parentNode;
            var parent = this;
            while (sortable.nodeName !== 'SORTABLE-JS') {
                parent = sortable;
                sortable = sortable.parentNode;
            }
            parent.remove();
            sortable.fire('update');
        });

    // Multi-selectable paper menus
    document.createElement('paper-menu').constructor.prototype.selectedData = function() {
        return $.map(this.selectedItems, function(x) {
            return (x.attributes['data-id'] || {}).value;
        });
    }

    $styles.applyAll();
});