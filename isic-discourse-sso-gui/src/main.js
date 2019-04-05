import '@babel/polyfill';
import 'url-polyfill';
import Vue from 'vue';

import '@/plugins/sentry';
import '@/plugins/vuetify';
import GirderProvider from '@/plugins/girder';
import App from '@/App.vue';

new Vue({
  render: h => h(App),
  provide: GirderProvider,
}).$mount('#app');
