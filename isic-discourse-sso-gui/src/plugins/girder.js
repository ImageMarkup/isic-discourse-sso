import Vue from 'vue';
import Girder, { RestClient } from '@girder/components/src';

// Install the Vue plugin that lets us use the components
Vue.use(Girder);

const girderRest = new RestClient({
  apiRoot: 'https://isic-archive.com/api/v1',
  // The "cors" setting is critical to setting the cookie and notifying the server of login
  cors: true,
});

const GirderProvider = {
  girderRest,
};

export default GirderProvider;
