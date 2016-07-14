(function () {
    "use strict";

    var _t = openerp._t;
    var _lt = openerp._lt;
    var QWeb = openerp.qweb;
    var xopgi_currency_rate = openerp.xopgi_currency_rate = {};

    xopgi_currency_rate.CurrencyConverter = openerp.Widget.extend({
        template: "currency_rate.CurrencyRate",

        events: {
            "change input.currency_amount": "calculateAmount",
            "change select.currency": "updateRate",
            "keydown input.currency_amount": function(eventObject){
                var key=eventObject.charCode || eventObject.keyCode;
                return(
                  key==8 ||                 //backspace
                  key==9 ||                 //tab
                  key==13 ||                //enter
                  key==46 ||                //delete
                  key==110 ||               //arrows
                  key==190 ||               //numbers
                  (key>=35 && key<=40) ||   //
                  (key>=48 && key<=57) ||   //keypad numbers
                  (key>=96 && key<=105)      //keypad numbers
                );
            },
            "keypress input.currency_amount": function(eventObject){
                var self = this;
                var keydown_internal_time= Date.now();
                self.keydown_time = keydown_internal_time;
                setTimeout( function() {
                    if(keydown_internal_time==self.keydown_time)
                        self.calculateAmount(eventObject);
                }, this.delay);
            },
            "click img.img-money_exchange": function(eventObject){
                var self = this;
                var id_currency_from = self.$("#currency_from").val();
                var id_currency_to = self.$("#currency_to").val();
                self.$("#currency_from").val(id_currency_to);
                self.$("#currency_to").val(id_currency_from);
                self.updateRate({target:{id:"currency_from_amount"}});
            },
            "show.bs.modal #myModalCurrencyRate": function(eventObject){
                var self = this;
                self.loadData();
            }
        },

        init: function(parent) {
            this._super(parent);
            this.currencies = [];
            this.decimal_precision = 5;
            this.delay = 600;
            this.keydown_time = 0;
            this.days_before = 7;
        },

        loadData: function() {
            var self = this;

            self.$("#currency_from_amount").val("");
            self.$("#currency_to_amount").val("");

            self.$("#currency_from").empty();
            self.$("#currency_to").empty();

            var date_from = new Date(Date.now() - this.days_before * 24 * 60 * 60 * 1000);
            var res_currency_rate = new openerp.web.Model("res.currency.rate");
            res_currency_rate.query(["currency_id", "rate", "name"])
                .filter([
                    '|',
                    ["name", ">", date_from.getFullYear()+"-"+date_from.getMonth()+"-"+date_from.getDate()],
                    ["rate", "=", 1]
                ])
                .order_by("currency_id", "-name")
                .all()
                .then(function (currencies_rate) {
                    var current_idcurrency="";
                    _.each(currencies_rate, function(currency_rate) {
                        if(current_idcurrency!=currency_rate.currency_id[0]){
                            current_idcurrency=currency_rate.currency_id[0];
                            self.$("#currency_from").append($('<option>', {value:self.currencies.length, text:currency_rate.currency_id[1]}));
                            self.$("#currency_to").append($('<option>', {value:self.currencies.length, text:currency_rate.currency_id[1]}));
                            self.currencies.push({idcurrency:current_idcurrency, currency:currency_rate.currency_id[1], rate:currency_rate.rate, date:currency_rate.name});
                        }
                    });
                    self.updateRate({target:{id:"currency_from_amount"}});
            });
        },
        getInternalRate: function(rate1, rate2){
            return rate1/rate2;
        },
        toFixed: function(value){
            return value.toFixed(this.decimal_precision);
        },
        updateRate: function(eventObject){
            var self = this;
            var id_currency_from = self.$("#currency_from").val();
            var id_currency_to = self.$("#currency_to").val();
            self.$(".currency_from_rate").text("1 " + self.currencies[id_currency_from].currency + " = " + self.toFixed(self.getInternalRate(self.currencies[id_currency_from].rate, self.currencies[id_currency_to].rate)) + " " + self.currencies[id_currency_to].currency);
            self.$(".currency_to_rate").text("1 " + self.currencies[id_currency_to].currency + " = " + self.toFixed(self.getInternalRate(self.currencies[id_currency_to].rate, self.currencies[id_currency_from].rate)) + " " + self.currencies[id_currency_from].currency);
            self.calculateAmount(eventObject);
        },

        calculateAmount: function(eventObject){
            var self = this;
            var id_currency_from = self.$("#currency_from").val();
            var id_currency_to = self.$("#currency_to").val();
            if(eventObject.target.id == "currency_to_amount"){
                self.$("#currency_from_amount").val(self.toFixed(self.getInternalRate(self.currencies[id_currency_to].rate, self.currencies[id_currency_from].rate)* self.$("#currency_to_amount").val()));
            }
            else{
                self.$("#currency_to_amount").val(self.toFixed(self.getInternalRate(self.currencies[id_currency_from].rate, self.currencies[id_currency_to].rate)* self.$("#currency_from_amount").val()));
            }
        }
    });

    if (openerp.web && openerp.web.UserMenu) {
        openerp.web.UserMenu.include({
            do_update: function () {
                var self = this;
                self.update_promise.then(function () {
                    var currencyRate = new openerp.xopgi_currency_rate.CurrencyConverter(this);
                    currencyRate.appendTo(window.$('.oe_systray'));
                });
                return this._super.apply(this, arguments);
            },
        });
    }

    return xopgi_currency_rate;
})();
