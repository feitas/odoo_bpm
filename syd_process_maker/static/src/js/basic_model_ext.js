odoo.define('syd_process_maker.BasicModel', function (require) {
    "use strict";
    var BasicModel = require('web.BasicModel');
    var BasicModelExt = BasicModel.include({
        /**
         * Create a request in the Process Maker
         *
         * @param {string} recordID id for a local resource
         * @returns
         */
        createResquest: async function (recordID) {
            var self = this;
            var record = this.localData[recordID];
            var context = this._getContext(record);
            return await this._rpc({
                model: 'syd_bpm.process',
                method: 'action_create_new_request',
                args: [record.data.id, record.model],
                context: context,
            }).then(function (res) {
                if (res.error) {
                    alert(res["message"]);
                } else {
                    location.reload();
                }
            }).catch(function () {
                throw Error("Ops, something wrong.....");
            });;
        },
    });

    return BasicModelExt;
});