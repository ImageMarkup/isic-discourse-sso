import Vue from 'vue';
import './plugins/vuetify'
import App from './App.vue';

Vue.config.productionTip = false;
import Girder, { RestClient } from '@girder/components';

// Install the Vue plugin that lets us use the components
Vue.use(Girder);

// apiRoot should point to your girder instance
const girderRest = new RestClient({ apiRoot: 'https://data.kitware.com/api/v1' });

// Provide "girderRest" to the root
new Vue({
  render: h => h(App),
  provide: { girderRest },
}).$mount('#app');

