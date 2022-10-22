odoo.define('syd_process_maker.FormController', function (require) {
    "use strict";

    var core = require('web.core');
    var FormController = require('web.FormController');

    var _t = core._t;
    var FormControllerExt = FormController.include({
        _getActionMenuItems: function (state) {
            if (!this.hasActionMenus || this.mode === 'edit') {
                return null;
            }
            const props = this._super(...arguments);
            const activeField = this.model.getActiveField(state);
            const otherActionItems = [];
            if (this.archiveEnabled && activeField in state.data) {
                if (state.data[activeField]) {
                    otherActionItems.push({
                        description: _t("Archive"),
                        callback: () => {
                            Dialog.confirm(this, _t("Are you sure that you want to archive this record?"), {
                                confirm_callback: () => this._toggleArchiveState(true),
                            });
                        },
                    });
                } else {
                    otherActionItems.push({
                        description: _t("Unarchive"),
                        callback: () => this._toggleArchiveState(false),
                    });
                }
            }
            if (this.activeActions.create && this.activeActions.duplicate) {
                otherActionItems.push({
                    description: _t("Duplicate"),
                    callback: () => this._onDuplicateRecord(this),
                });
            }
            if (this.activeActions.delete) {
                otherActionItems.push({
                    description: _t("Delete"),
                    callback: () => this._onDeleteRecord(this),
                });
            }
            otherActionItems.push({
                description: _t("Create Resquest"),
                callback: () => this._onCreateResquest(this),
            });
            return Object.assign(props, {
                items: Object.assign(this.toolbarActions, { other: otherActionItems }),
            });
        },

        /**
         * Called when the user clicks on 'Create Request' in the action menus
         *
         * @overwrite
         * @private
         */
        _onCreateResquest: async function () {
            const handle = await this.model.createResquest(this.handle);
        },
    })

    return FormControllerExt;

});
