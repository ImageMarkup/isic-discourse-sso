import $ from 'jquery';

import View from 'girder/views/View';
import { login } from 'girder/auth';
import { restRequest } from 'girder/rest';
import 'girder/utilities/jquery/girderEnable';

import OAuthLoginView from 'girder_plugins/oauth/views/OAuthLoginView';

import LoginDialogTemplate from 'girder/templates/layout/loginDialog.pug';

const StandaloneLoginView = View.extend({
    events: {
        'submit #g-login-form': function (e) {
            e.preventDefault();

            this.$('#g-login-button').girderEnable(false);
            this.$('.g-validation-failed-message').text('');

            login(this.$('#g-login').val(), this.$('#g-password').val())
                .done((resp) => {
                    window.location.reload(true);
                })
                .fail((err) => {
                    this.$('.g-validation-failed-message').text(err.responseJSON.message);

                    if (err.responseJSON.extra === 'emailVerification') {
                        var html = err.responseJSON.message +
                            ' <a class="g-send-verification-email">Click here to send verification email.</a>';
                        $('.g-validation-failed-message').html(html);
                    }
                })
                .always(() => {
                    this.$('#g-login-button').girderEnable(true);
                });
        },

        'click .g-send-verification-email': function () {
            this.$('.g-validation-failed-message').html('');
            restRequest({
                url: 'user/verification',
                method: 'POST',
                data: {login: this.$('#g-login').val()},
                error: null
            })
                .done((resp) => {
                    this.$('.g-validation-failed-message').html(resp.message);
                })
                .fail((err) => {
                    this.$('.g-validation-failed-message').html(err.responseJSON.message);
                });
        },

        'click a.g-register-link': function () {
            window.location.assign('https://isic-archive.com/');
        },

        'click a.g-forgot-password': function () {
            window.location.assign('https://isic-archive.com/');
        }
    },

    render: function () {
        this.$el.html(LoginDialogTemplate({
            enablePasswordLogin: true,
            // TODO: fetch registrationPolicy from the server; for now, null will default to "open"
            registrationPolicy: null
        }));
        this.$('close').remove();
        this.$('[data-dismiss="modal"]').remove();
        this.$('.modal-title').text('ISIC Archive: Log in');

        this.oauthLoginView = new OAuthLoginView({
            redirect: window.location.href,
            el: this.$('.modal-body'),
            parentView: this
        }).render();

        return this;
    }
});

const loginView = new StandaloneLoginView({
    el: $('body'),
    parentView: null
});
loginView.render();
