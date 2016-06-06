(function () {
    "use strict";

    var _t = openerp._t;
    var _lt = openerp._lt;
    var QWeb = openerp.qweb;
    var instance = openerp;
    var xopgi_distance_calculator = openerp.xopgi_distance_calculator = {};

    xopgi_distance_calculator.ViewDistanceCalculator = openerp.Widget.extend({
        template: "distance_calculator.ViewDistanceCalculator",
        events: {
            "change select": function(eventObject){
                if(eventObject.target.value=="0")
                    $(eventObject.target).addClass("not_chosen");
                else
                    $(eventObject.target).removeClass("not_chosen");
            },
            "change select.country": "loadStates",
            "change select.state": "loadRoutePoints",
            "change select.route_point": "loadDistance",
            "click img.img-add_route": "addRoute",
            "click img.img-delete_route": "deleteRoute",
            "keydown .distance": function(eventObject){
                var self = this;
                var key=eventObject.charCode || eventObject.keyCode;
                if(key==9 && $(eventObject.target).closest('tr').is(':last-child'))  //tab in last row
                    self.addRoute();
            },
            "click button.accept_distance": "accept_distance"
        },
        init: function(parent) {
            this._super(parent);
        },
        start: function () {
            var self = this;

            self.$(".country").append($('<option>', {value:0, text:"- Select -"}));

            var res_country = new openerp.web.Model("res.country");
            res_country.query(["id", "name"])
                .all()
                .then(function (countries) {
                    _.each(countries, function(country) {
                        self.$(".country").append($('<option>', {value:country.id, text:country.name}));
                    });
                    self.$(".country").val(52);
                    self.$(".country").removeClass("not_chosen");
            });
        },
        loadData: function () {
            var self = this;
            self.$(".tbodyRoutes").children('tr:not(:first)').remove();
            self.loadStates();
        },
        loadStates: function () {
            var self = this;

            self.$(".origin").empty();
            self.$(".destination").empty();

            self.$(".origin").append($('<option>', {value:0, text:"- Select -"}));
            self.$(".destination").append($('<option>', {value:0, text:"- Select -"}));

            self.$(".origin").addClass("not_chosen");
            self.$(".destination").addClass("not_chosen");

            self.$(".distance").val("");
            self.$(".total_distance").val("");

            var country_id=self.$(".country").val();
            if(country_id!=0){
                var res_states = new openerp.web.Model("res.country.state");
                res_states.query(["id", "name"])
                    .filter([["country_id.id","=", country_id]])
                    .all()
                    .then(function (states) {
                        _.each(states, function(state) {
                            self.$(".state").append($('<option>', {value:state.id, text:state.name}));
                        });
                });
            }
        },
        loadRoutePoints: function (eventObject) {
            var self = this;
            var route_point_target;

            if(self.$(eventObject.target).is(".origin"))
                route_point_target=self.$(eventObject.target.parentNode.parentNode.children[2].children[0]);
            else
                route_point_target=self.$(eventObject.target.parentNode.parentNode.children[6].children[0]);

            route_point_target.empty();
            route_point_target.append($('<option>', {value:0, text:"- Select -"}));
            route_point_target.addClass("not_chosen");

            var state_id=self.$(eventObject.target).val();
            if(state_id!=0){
                var res_route_points = new openerp.web.Model("res.route.points");
                res_route_points.query(["id", "name", "is_state_reference"])
                    .filter([["state_id.id","=", state_id]])
                    .all()
                    .then(function (route_points) {
                        var state_reference=0;
                        _.each(route_points, function(route_point) {
                            if(state_reference==0 && route_point.is_state_reference)
                                state_reference=route_point.id;
                            route_point_target.append($('<option>', {value:route_point.id, text:route_point.name}));
                        });
                        if(state_reference!=0){
                            route_point_target.val(state_reference);
                            route_point_target.removeClass("not_chosen");
                            self.loadDistance(eventObject);
                        }
                });
            }

            eventObject.target.parentNode.parentNode.children[8].children[0].value="";
            self.calculateDistance();
        },
        addRoute: function(){
            var self = this;
            $(".tbodyRoutes tr:first").clone().appendTo(".tblRoutes");
            self.$(".tbodyRoutes tr:last .route_point").empty();
            self.$(".tbodyRoutes tr:last .route_point").append($('<option>', {value:0, text:"- Select -"}));
            self.$(".tbodyRoutes tr:last .origin").addClass("not_chosen");
            self.$(".tbodyRoutes tr:last .destination").addClass("not_chosen");
            self.$(".tbodyRoutes tr:last .distance").val("");
            self.calculateDistance();
        },
        deleteRoute: function(eventObject){
            var self = this;
            if(self.$(".tbodyRoutes").children().length==1){
                self.$(".route_point").empty();
                self.$(".route_point").append($('<option>', {value:0, text:"- Select -"}));
                self.$(".origin").val("0");
                self.$(".destination").val("0");
                self.$(".origin").addClass("not_chosen");
                self.$(".destination").addClass("not_chosen");
                self.$(".distance").val("");
            }
            else
                eventObject.target.parentNode.parentNode.remove();
            self.calculateDistance();
        },
        loadDistance: function(eventObject){
            var self = this;

            var origin_point_id=eventObject.target.parentNode.parentNode.children[2].children[0].value;
            var destination_state_id=eventObject.target.parentNode.parentNode.children[4].children[0].value;
            var destination_point_id=eventObject.target.parentNode.parentNode.children[6].children[0].value;

            if(origin_point_id=="0" || destination_point_id=="0"){
                eventObject.target.parentNode.parentNode.children[8].children[0].value="";
                self.calculateDistance();
            }
            else{
                var res_routes = new openerp.web.Model("res.routes");
                res_routes.query(["distance"])
                    .filter([["origin_point_id.id","=", origin_point_id],["destination_point_id.id","=", destination_point_id]])
                    .first()
                    .then(function (route) {
                        eventObject.target.parentNode.parentNode.children[8].children[0].value=(route==null)?"":route.distance;
                        self.calculateDistance();
                });
                if($(eventObject.target).closest('tr').is(':last-child')){
                    self.addRoute();
                    $(".tbodyRoutes tr:last .state.origin").val(destination_state_id);
                    $(".tbodyRoutes tr:last .route_point.origin").empty();
                    $(".tbodyRoutes tr:last .route_point.origin").append(self.$(eventObject.target.parentNode.parentNode.children[6].children[0]).children().clone());
                    $(".tbodyRoutes tr:last .route_point.origin").val(destination_point_id);
                    $(".tbodyRoutes tr:last .origin").removeClass("not_chosen");
                }
            }
        },
        calculateDistance: function(){
            var self = this;
            var total_distance=0;
            self.$(".distance").each(function(index, element) {
                total_distance+=Number(element.value);
            });
            self.$(".total_distance").val(total_distance);
        },
        show: function() {
            this.$el.modal();
            this.loadData();
        },
        hide: function(){
            this.$el.modal();
        },
        accept_distance: function(){
            var self = this;
            this.trigger("accept_distance", self.$(".total_distance").val());
        }
    });

    xopgi_distance_calculator.DistanceCalculatorTopButton = openerp.Widget.extend({
        template:'distance_calculator.DistanceCalculatorTopButton',
        events: {
            "click": "clicked"
        },
        clicked: function(ev) {
            ev.preventDefault();
            this.trigger("clicked");
        }
    });

    instance.web.form.FieldDistanceCalculator = instance.web.form.FieldFloat.extend({
        template: "FieldDistanceCalculator",
        widget_class: "oe_form_field_float oe_form_distance_calculator",
        events: {
            "click img.open_distance_calculator": "open_modal"
        },
        init: function () {
            var self = this;
            this._super.apply(this, arguments);
            var widget = new openerp.xopgi_distance_calculator.ViewDistanceCalculator(this);
            widget.appendTo(self.$(".oe_distance_calculator_view"));
            widget.on("accept_distance", self, self.accept_distance);
            this.modal = widget;
        },
        renderElement: function () {
            var self = this;
            this._super();
        },
        open_modal: function(){
            this.modal.show();
        },
        accept_distance: function (distance) {
            var self = this;
            self.set_value(distance);
        }
    });

    instance.web.form.widgets.add('float_distance_calculator', 'instance.web.form.FieldDistanceCalculator');

    if (openerp.web && openerp.web.UserMenu) {
        openerp.web.UserMenu.include({
            do_update: function () {
                var self = this;
                self.update_promise.then(function () {
                    var view = new openerp.xopgi_distance_calculator.ViewDistanceCalculator(self);
                    view.appendTo(openerp.client.$el);
                    var button = new openerp.xopgi_distance_calculator.DistanceCalculatorTopButton(this);
                    button.on("clicked", view, view.show);
                    button.appendTo(window.$('.oe_systray'));
                });
                return this._super.apply(this, arguments);
            }
        });
    }

    return xopgi_distance_calculator;
})();
