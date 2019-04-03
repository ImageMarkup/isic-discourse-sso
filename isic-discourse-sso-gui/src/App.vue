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
  created() {
    this.girderRest.$on('login', this.onLogin);
  },
  methods: {
    onLogin() {
      window.location.reload(true);
    },
  },
};
</script>
