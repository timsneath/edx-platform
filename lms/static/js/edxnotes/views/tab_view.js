;(function (define, undefined) {
'use strict';
define([
    'underscore', 'backbone', 'js/edxnotes/models/tab'
], function (_, Backbone, TabModel) {
    var TabView = Backbone.View.extend({
        PanelConstructor: null,

        tabInfo: {
            name: '',
            class_name: ''
        },

        initialize: function (options) {
            _.bindAll(this, 'showLoadingIndicator', 'hideLoadingIndicator');
            this.options = _.defaults(options || {}, {
                createTabOnInitialization: true
            });

            if (this.options.createTabOnInitialization) {
                this.createTab();
            }
        },

        /**
         * Creates a tab for the view.
         */
        createTab: function () {
            this.tabModel = new TabModel(this.tabInfo);
            this.options.tabsCollection.add(this.tabModel);
            this.listenTo(this.tabModel, {
                'change:is_active': function (model, value) {
                    if (value) {
                        this.render();
                    } else {
                        this.destroySubView();
                    }
                },
                'destroy': function () {
                    this.destroySubView();
                    this.tabModel = null;
                    this.onClose();
                }
            });
        },

        /**
         * Renders content for the view.
         */
        render: function () {
            this.showLoadingIndicator();
            // If the view is already rendered, destroy it.
            this.destroySubView();
            this.renderContent().always(this.hideLoadingIndicator);
            return this;
        },

        renderContent: function () {
            this.contentView = this.getSubView();
            this.$('.wrapper-tabs').append(this.contentView.render().$el);
            return $.Deferred().resolve().promise();
        },

        getSubView: function () {
            var collection = this.getCollection();
            return new this.PanelConstructor({collection: collection});
        },

        destroySubView: function () {
            if (this.contentView) {
                this.contentView.remove();
                this.contentView = null;
            }
        },

        /**
         * Returns collection for the view.
         * @return {Backbone.Collection}
         */
        getCollection: function () {
            return this.collection;
        },

        /**
         * Callback that is called on closing the tab.
         */
        onClose: function () { },

        /**
         * Shows the page's loading indicator.
         */
        showLoadingIndicator: function() {
            this.$('.ui-loading').removeClass('is-hidden');
        },

        /**
         * Hides the page's loading indicator.
         */
        hideLoadingIndicator: function() {
            this.$('.ui-loading').addClass('is-hidden');
        },


        /**
         * Shows error message.
         */
        showErrorMessage: function (message) {
            this.$('.inline-error')
                .text(message)
                .removeClass('is-hidden');
        },

        /**
         * Hides error message.
         */
        hideErrorMessage: function () {
            this.$('.inline-error')
                .text('')
                .addClass('is-hidden');
        }
    });

    return TabView;
});
}).call(this, define || RequireJS.define);
