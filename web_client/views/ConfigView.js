import PluginConfigBreadcrumbWidget from 'girder/views/widgets/PluginConfigBreadcrumbWidget';
import View from 'girder/views/View';
import events from 'girder/events';
import { restRequest } from 'girder/rest';

import ConfigViewTemplate from '../templates/configView.pug';
import '../stylesheets/configView.styl'

const ConfigView = View.extend({
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
        restRequest({
            type: 'GET',
            path: 'system/setting',
            data: {
                list: JSON.stringify([
                    'discourse_sso.sso_secret',
                    'discourse_sso.require_activation'
                ])
            }
        })
            .done((resp) => {
                this.render();
                this.$('#g-discourse-sso-sso-secret').val(
                    resp['discourse_sso.sso_secret']);
                this.$('#g-discourse-sso-require-activation').prop(
                    'checked',
                    resp['discourse_sso.require_activation']);
            });
    },

    render: function () {
        this.$el.html(ConfigViewTemplate());

        if (!this.breadcrumb) {
            this.breadcrumb = new PluginConfigBreadcrumbWidget({
                pluginName: 'Discourse SSO',
                el: this.$('.g-config-breadcrumb-container'),
                parentView: this
            });
        }

        this.breadcrumb.render();

        return this;
    },

    _saveSettings: function (settings) {
        restRequest({
            type: 'PUT',
            path: 'system/setting',
            data: {
                list: JSON.stringify(settings)
            },
            error: null
        })
            .done(() => {
                events.trigger('g:alert', {
                    icon: 'ok',
                    text: 'Settings saved.',
                    type: 'success',
                    timeout: 4000
                });
            })
            .error((resp) => {
                this.$('#g-discourse-sso-error-message').text(
                    resp.responseJSON.message
                );
            });
    }
});

export default ConfigView;
