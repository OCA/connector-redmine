openerp.redmine_import_time_entry = function(instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.hr_timesheet_sheet.WeeklyTimesheet = instance.hr_timesheet_sheet.WeeklyTimesheet.extend({
        ignore_fields: function() {
            // See README.rst for the reason to remove partner_id and company_id from
            // the fields to save. Those fields are related to the fields on the analytic account.
            return ['line_id', 'partner_id', 'company_id'];
        },
        update_sheets: function() {
            var self = this;
            if (self.querying)
                return;
            self.updating = true;

            var new_timesheets = _(self.get("sheets"));
            var res = [];

            new_timesheets.forEach(function(new_ts){
                if(new_ts.id === undefined){
                    if(new_ts.unit_amount !== 0){
                        // New record
                        res.push([0, 0, new_ts]);
                    }
                }
                else if(new_ts.unit_amount !== 0){
                    res.push([1, new_ts.id, new_ts]);
                }
                else{
                    res.push([2, new_ts.id]);
                }
            });

            self.field_manager.set_values({timesheet_ids: res}).done(function() {
                self.updating = false;
            });
        },
        generate_o2m_value: function() {
            var self = this;
            var ops = [];
            var ignored_fields = self.ignore_fields();
            _.each(self.accounts, function(account) {
                _.each(account.days, function(day) {
                    _.each(day.lines, function(line) {
                        var tmp = _.clone(line);

                        // The following line was removed from the method
                        // tmp.id = undefined;

                        _.each(line, function(v, k) {
                            if (v instanceof Array) {
                                tmp[k] = v[0];
                            }
                        });

                        tmp = _.omit(tmp, ignored_fields);

                        ops.push(tmp);
                    });
                });
            });
            return ops;
        },
    });
};
