odoo.define('xopgi_account_advancement.advance_account', function (require) {
"use strict";

var core = require('web.core');
var form_common = require('web.form_common');
var formats = require('web.formats');
var Model = require('web.Model');

var QWeb = core.qweb;
var _t = core._t;

var ShowAccountAdvanceLineWidget = form_common.AbstractField.extend({
    render_value: function() {
        var self = this;
        var info = JSON.parse(this.get('value'));
        var invoice_id = info.invoice_id;
        var partner_id = info.partner_id;
        var type_account = info.title;

        if (info !== false) {
            _.each(info.content, function(k,v){
                k.index = v;
                k.amount = formats.format_value(
                    k.amount,
                    {type: "float", digits: k.digits}
                );
                if (k.date){
                    k.date = formats.format_value(k.date, {type: "date"});
                }
            });
            this.$el.html(QWeb.render('ShowAdvanceAccountInfo', {
                'lines': info.content,
                'title': info.title
            }));
            this.$('.lower').click(function(){
                var account_id = $(this).data('id') || false;
                var amount = $(this).data('max_reduction') || false;
                var model = new Model("account.invoice");
                model.call("match_advance_account",
                           [invoice_id, account_id, amount])
                     .then(function(result){
                        self.view.reload();
                     });
            });
        }
        else {
            this.$el.html('');
        }
    },
});

core.form_widget_registry.add(
   'advance_account',
   ShowAccountAdvanceLineWidget
);

});
