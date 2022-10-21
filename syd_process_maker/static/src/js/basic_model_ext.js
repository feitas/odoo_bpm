odoo.define('syd_process_maker.BasicModel', function (require) {
    "use strict";
    var BasicModel = require('web.BasicModel');
    var BasicModelExt = BasicModel.include({
        /**
         * Duplicate a record (by calling the 'copy' route)
         *
         * @param {string} recordID id for a local resource
         * @returns {Promise<string>} resolves to the id of duplicate record
         */
        createResquest: async function (recordID) {
            var self = this;
            var record = this.localData[recordID];
            var context = this._getContext(record);
            return await this._rpc({
                model: 'syd_bpm.process_group',
                method: 'start_process',
                args: [record.data.id, record.model],
                context: context,
            }).then(function (res_id) {
                var index = record.res_ids.indexOf(record.res_id);
                record.res_ids.splice(index + 1, 0, res_id);
                return self.load({
                    fieldsInfo: record.fieldsInfo,
                    fields: record.fields,
                    modelName: record.model,
                    res_id: res_id,
                    res_ids: record.res_ids.slice(0),
                    viewType: record.viewType,
                    context: context,
                });
            }).catch(function () {
                throw Error("Calling _rpc on a destroyed widget should return a " +
                    "promise that remains pending forever");
            });;
        },
    });

    return BasicModelExt;
});