import 'url-polyfill';
import Vue from 'vue';

import '@/plugins/sentry';
import GirderProvider from '@/plugins/girder';
import { vuetify } from '@girder/components/src';
import App from '@/App.vue';

new Vue({
  render: (h) => h(App),
  provide: GirderProvider,
  vuetify,
}).$mount('#app');
