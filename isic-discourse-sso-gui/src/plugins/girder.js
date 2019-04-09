import Vue from 'vue';
import Girder, { RestClient } from '@girder/components/src';

// Install the Vue plugin that lets us use the components
Vue.use(Girder);

const girderRest = new RestClient({
  apiRoot: process.env.VUE_APP_ISIC_API_ROOT,
  // Do not overwrite the cookie in Javascript; it will be set with a Domain attribute by HTTP
  cors: false,
});

girderRest.interceptors.request.use(config => ({
  ...config,
  // Send and receive cookies
  withCredentials: true,
}));

const GirderProvider = {
  girderRest,
};

export default GirderProvider;
