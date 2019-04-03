import '@babel/polyfill';
import 'url-polyfill';
import Vue from 'vue';
import App from '@/App.vue';

import '@/plugins/vuetify';
import GirderProvider from '@/plugins/girder';

new Vue({
  render: h => h(App),
  provide: GirderProvider,
}).$mount('#app');
