define(
    ["backbone", "i18n"],
    function(Backbone, i18n) {
        "use strict";

        var statusStrings = {
            // Translators: This is the status of a video upload that is queued
            // waiting for other uploads to complete
            STATUS_QUEUED: i18n.gettext("Queued"),
            // Translators: This is the status of an active video upload
            STATUS_UPLOADING: i18n.gettext("Uploading"),
            // Translators: This is the status of a video upload that has
            // completed successfully
            STATUS_COMPLETED: i18n.gettext("Upload completed"),
            // Translators: This is the status of a video upload that has failed
            STATUS_FAILED: i18n.gettext("Upload failed")
        };

        var ActiveVideoUpload = Backbone.Model.extend(
            {
                defaults: {
                    status: statusStrings.STATUS_QUEUED
                }
            },
            statusStrings
        );

        return ActiveVideoUpload;
    }
);
