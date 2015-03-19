openerp.xopgi_account = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.account = instance.web.account || {};
    instance.web.account.ReconciliationListView.include({
        /* Makes that when clicking over an item in the conciliation viewlist
           it opens the entry to be able to inspect it. */
        do_activate_record: function(index, id, dataset, view) {
            this._super.apply(this, arguments);
            var self = this;
            var pop = new instance.web.form.FormOpenPopup(self);
            pop.show_element('account.move.line', id, {}, {
                readonly: true
            });
        },
    });
}
