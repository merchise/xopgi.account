(function () {
    "use strict";

    var _t = openerp._t;
    var _lt = openerp._lt;
    var QWeb = openerp.qweb;
    var xopgi_distance_calculator = openerp.xopgi_distance_calculator = {};

    xopgi_distance_calculator.DistanceCalculator = openerp.Widget.extend({
        template: "distance_calculator.DistanceCalculator",
        events: {
            "change select.origin": "findDistance",
            "change select.destination": "findDistance",
            "click img.img-add_route": "addRoute",
            "click img.img-delete_route": "deleteRoute"
        },
        init: function(parent) {
            this._super(parent);
            this.days_before = 365*2;
        },
        start: function () {
            var self = this;

            self.$(".origin").append($('<option>', {value:0, text:"- Select -"}));
            self.$(".destination").append($('<option>', {value:0, text:"- Select -"}));

            var res_route_points = new openerp.web.Model("res.route.points");
            res_route_points.query(["id", "name"])
                .all()
                .then(function (route_points) {
                    _.each(route_points, function(route_point) {
                            self.$(".origin").append($('<option>', {value:route_point.id, text:route_point.name}));
                            self.$(".destination").append($('<option>', {value:route_point.id, text:route_point.name}));
                    });
            });
        },
        addRoute: function(){
            var self = this;
            $("#tbodyRoutes tr:first").clone().appendTo("#tblRoutes");
            self.$("#tbodyRoutes tr:last .origin").addClass("not_chosen");
            self.$("#tbodyRoutes tr:last .destination").addClass("not_chosen");
            self.$("#tbodyRoutes tr:last .distance").val("");
            self.calculateDistance();
        },
        deleteRoute: function(eventObject){
            var self = this;
            if(self.$("#tbodyRoutes").children().length==1){
                self.$(".origin").val("0");
                self.$(".destination").val("0");
                self.$(".distance").val("");
            }
            else
                eventObject.target.parentNode.parentNode.remove();
            self.calculateDistance();
        },
        findDistance: function(eventObject){
            var self = this;

            if(eventObject.target.value=="0")
                eventObject.target.className += " not_chosen";
            else
                eventObject.target.className = eventObject.target.className.replace("not_chosen", "");

            var origin_point_id=eventObject.target.parentNode.parentNode.children[0].children[0].value;
            var destination_point_id=eventObject.target.parentNode.parentNode.children[2].children[0].value;

            if(origin_point_id=="0" || destination_point_id=="0"){
                eventObject.target.parentNode.parentNode.children[4].children[0].value="";
                self.calculateDistance();
            }
            else{
                var res_routes = new openerp.web.Model("res.routes");
                res_routes.query(["distance"])
                    .filter([["origin_point_id.id","=", origin_point_id],["destination_point_id.id","=", destination_point_id]])
                    .first()
                    .then(function (route) {
                        eventObject.target.parentNode.parentNode.children[4].children[0].value=(route==null)?"":route.distance;
                        self.calculateDistance();
                });
            }
        },
        calculateDistance: function(){
            var self = this;
            var total_distance=0;
            self.$(".distance").each(function(index, element) {
                total_distance+=Number(element.value);
            });
            self.$(".total_distance").val(total_distance);
        }
    });

    if (openerp.web && openerp.web.UserMenu) {
        openerp.web.UserMenu.include({
            do_update: function () {
                var self = this;
                self.update_promise.then(function () {
                    var distancecalculator = new openerp.xopgi_distance_calculator.DistanceCalculator(this);
                    distancecalculator.appendTo(window.$('.oe_systray'));
                });
                return this._super.apply(this, arguments);
            },
        });
    }

    return xopgi_distance_calculator;
})();

