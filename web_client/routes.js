/* eslint-disable import/first */

import router from 'girder/router';
import events from 'girder/events';
import { exposePluginConfig } from 'girder/utilities/PluginUtils';

exposePluginConfig('discourse_sso', 'plugins/discourse_sso/config');

import ConfigView from './views/ConfigView';
router.route('plugins/discourse_sso/config', 'discourseSsoConfig', () => {
    events.trigger('g:navigateTo', ConfigView);
});
