<template>
  <v-app>
    <v-content>
      <Authentication :oauth="true"/>
    </v-content>
  </v-app>
</template>

<script>
import Authentication from '@girder/components/src/components/Authentication';

export default {
  name: 'App',
  components: {
    Authentication,
  },
  data () {
    return {
      //
    }
  }
}
</script>
