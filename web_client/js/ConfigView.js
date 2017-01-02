/**
* Administrative configuration view.
*/
girder.views.discourse_sso_ConfigView = girder.View.extend({
    events: {
        'submit #g-discourse-sso-settings-form': function (event) {
            event.preventDefault();

            this.$('#g-discourse-sso-error-message').empty();

            this._saveSettings([{
                key: 'discourse_sso.sso_secret',
                value: this.$('#g-discourse-sso-sso-secret').val().trim()
            }, {
                key: 'discourse_sso.require_activation',
                value: this.$('#g-discourse-sso-require-activation').prop('checked')
            }]);
        }
    },

    initialize: function () {
        girder.restRequest({
            type: 'GET',
            path: 'system/setting',
            data: {
                list: JSON.stringify([
                    'discourse_sso.sso_secret',
                    'discourse_sso.require_activation'
                ])
            }
        }).done(_.bind(function (resp) {
            this.render();
            this.$('#g-discourse-sso-sso-secret').val(
                resp['discourse_sso.sso_secret']);
            this.$('#g-discourse-sso-require-activation').prop(
                'checked',
                resp['discourse_sso.require_activation']);
        }, this));
    },

    render: function () {
        this.$el.html(girder.templates.discourse_sso_config());

        if (!this.breadcrumb) {
            this.breadcrumb = new girder.views.PluginConfigBreadcrumbWidget({
                pluginName: 'Discourse SSO',
                el: this.$('.g-config-breadcrumb-container'),
                parentView: this
            });
        }

        this.breadcrumb.render();

        return this;
    },

    _saveSettings: function (settings) {
        girder.restRequest({
            type: 'PUT',
            path: 'system/setting',
            data: {
                list: JSON.stringify(settings)
            },
            error: null
        }).done(_.bind(function () {
            girder.events.trigger('g:alert', {
                icon: 'ok',
                text: 'Settings saved.',
                type: 'success',
                timeout: 4000
            });
        }, this)).error(_.bind(function (resp) {
            this.$('#g-discourse-sso-error-message').text(
                resp.responseJSON.message
            );
        }, this));
    }
});

girder.router.route('plugins/discourse_sso/config', 'discourseSsoConfig', function () {
    girder.events.trigger('g:navigateTo', girder.views.discourse_sso_ConfigView);
});
