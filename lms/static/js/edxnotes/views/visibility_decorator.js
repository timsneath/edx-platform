;(function (define, undefined) {
'use strict';
define([
    'jquery', 'underscore', 'js/edxnotes/views/notes_factory'
], function($, _, NotesFactory) {
    var parameters = {}, visibility = null,
        getIds, createNote, cleanup, notesLoaded, factory;

        getIds = function () {
            return _.map($('.edx-notes-wrapper'), function (element) {
                return element.id;
            });
        };

        createNote = function (element, params) {
            if (params) {
                return NotesFactory.factory(element, params);
            }
            return null;
        };

        cleanup = function (ids) {
            var list = _.clone(Annotator._instances);
            ids = ids || [];

            _.each(list, function (instance) {
                var id = instance.element.attr('id');
                if (!_.contains(ids, id)) {
                    instance.unsubscribe("annotationsLoaded", notesLoaded);
                    instance.destroy();
                }
            });
        };

        notesLoaded = function (notes) {
            var highlight, offset, event, hash = window.location.hash.substr(1);

            _.each(notes, function (note) {
                if (note.id === hash) {
                    highlight = $('span.annotator-hl:contains('+note.quote+')');
                    $('html, body').animate({scrollTop: highlight.offset().top}, 'slow');
                    offset = highlight.offset();
                    event = $.Event('click', {
                        pageX: offset.left,
                        pageY: offset.top
                    });
                    highlight.trigger(event);
                }
            });
        };

        factory = function (element, params, isVisible) {
            var note;
            // When switching sequentials, we need to keep track of the
            // parameters of each element and the visibility (that may have been
            // changed by the checkbox).
            parameters[element.id] = params;

            if (_.isNull(visibility)) {
                visibility = isVisible;
            }

            if (visibility) {
                // When switching sequentials, the global object Annotator still
                // keeps track of the previous instances that were created in an
                // array called 'Annotator._instances'. We have to destroy these
                // but keep those found on page being loaded (for the case when
                // there are more than one HTMLcomponent per vertical).
                cleanup(getIds());
                note = createNote(element, params);
                // If the page URL contains a hash, we could be coming from a
                // click on an anchor in the notes page. In that case, the hash
                // is the id of the note that has to be scrolled to and opened.
                if (window.location.hash.substr(1)) {
                    note.subscribe("annotationsLoaded", notesLoaded);
                }
                return note;
            }
            return null;
        };

    return {
        factory: factory,

        enableNote: function (element) {
            createNote(element, parameters[element.id]);
            visibility = true;
        },

        disableNotes: function () {
            cleanup();
            visibility = false;
        },

        _setVisibility: function (state) {
            visibility = state;
        },
    }
});
}).call(this, define || RequireJS.define);
