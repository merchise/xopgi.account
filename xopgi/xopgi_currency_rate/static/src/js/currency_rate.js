(function () {
    "use strict";

    var _t = openerp._t;
    var _lt = openerp._lt;
    var QWeb = openerp.qweb;
    var xopgi_currency_rate = openerp.xopgi_currency_rate = {};

    var CurrencyConverter = openerp.Widget.extend({
        template: "CurrencyRate",
        events: {
            "change input.fromeur": function(){
                var amount = self.$(".fromeur").val();
                self.$(".tousd").text("= " + this.getInternalRate(this.usd.rate, this.eur.rate) * amount + " USD");
            },
            "change input.fromusd": function(){
                var amount = self.$(".fromusd").val();
                self.$(".toeur").text("= " + this.getInternalRate(this.eur.rate, this.usd.rate) * amount + " EUR");
            }
        },
        start: function () {
            var self = this;
            this.eur = {};
            this.usd = {};
            var res_currency_rate = new openerp.web.Model("res.currency.rate");
            res_currency_rate.query(["name", "rate"]).filter([["currency_id.name", "=", "EUR"]])
                .order_by("-name", "-id").first().then(function (eur_rate) {
                self.eur = eur_rate;
                res_currency_rate.query(["name", "rate"]).filter([["currency_id.name", "=", "USD"]])
                    .order_by("-name", "-id").first().then(function (usd_rate) {
                    self.usd = usd_rate;
                    self.$(".eurdate").text("Last EUR Update: " + self.eur.name);
                    self.$(".eurrate").text("1 EUR = " + self.getInternalRate(self.usd.rate, self.eur.rate) + " USD");
                    self.$(".usddate").text("Last USD Update: " + self.usd.name);
                    self.$(".usdrate").text("1 USD = " + self.getInternalRate(self.eur.rate, self.usd.rate) + " EUR");
                });
            });
        },
        getInternalRate: function(rate1, rate2){
            return Math.round(rate1/rate2*10000)/10000.0;
        }
    });

    xopgi_currency_rate.CurrencyRate = CurrencyConverter;

    if (openerp.web && openerp.web.UserMenu) {
        openerp.web.UserMenu.include({
            do_update: function () {
                var self = this;
                self.update_promise.then(function () {
                    var currencyRate = new CurrencyConverter(this);
                    currencyRate.appendTo(window.$('.oe_systray'));
                });
                return this._super.apply(this, arguments);
            },
        });
    }

    return xopgi_currency_rate;
})();