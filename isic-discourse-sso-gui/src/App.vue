<template>
  <v-app>
    <v-content>
      <v-container>
        <v-layout>
          <v-flex
            xs6
            offset-xs3
          >
            <div class="display-2">
              ISIC Forum Login
            </div>

            <template v-if="errorText !== null">
              <v-alert
                :value="true"
                type="error"
              >
                Error: {{ errorText }}
              </v-alert>
            </template>

            <template v-else-if="mustLogin">
              <div class="my-3 subheading">
                To login to the
                <a
                  href="https://forum.isic-archive.com/"
                  target="_blank"
                  rel="noreferrer noopener"
                >ISIC Forum</a>,
                use or create an account on the
                <a
                  href="https://www.isic-archive.com/"
                  target="_blank"
                  rel="noreferrer noopener"
                >ISIC Archive</a>:
              </div>
              <Authentication
                :register="true"
                :oauth="false"
              />
            </template>

            <template v-else>
              <div class="my-3 subheading">
                Loading...
              </div>
              <v-progress-circular indeterminate />
            </template>
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import Authentication from '@girder/components/src/components/Authentication';

export default {
  name: 'App',
  inject: ['girderRest'],
  components: {
    Authentication,
  },
  data() {
    return {
      mustLogin: false,
      errorText: null,
    };
  },
  created() {
    this.girderRest.$on('login', this.onLogin);

    this.tryRedirect();
  },
  methods: {
    onLogin() {
      this.tryRedirect();
    },
    async tryRedirect() {
      this.mustLogin = false;
      this.errorText = null;

      const currentQs = (new URL(document.location)).searchParams;

      let discourseSso;
      try {
        discourseSso = await this.girderRest.request({
          url: 'discourse_sso',
          method: 'get',
          // Pass along the current query string unchanged
          params: currentQs,
        });
      } catch (error) {
        if (error.response && error.response.status === 401) {
          // Normal failure
          this.mustLogin = true;
        } else {
          if (error.response) {
            // Abnormal application failure
            const responseData = error.response.data;
            this.errorText = responseData.message || JSON.stringify(responseData);
          } else {
            // Abnormal network failure
            this.errorText = error.message;
          }
          throw error;
        }
        return;
      }
      // Success
      window.location.replace(discourseSso.data.returnUrl);
    },
  },
};
</script>
