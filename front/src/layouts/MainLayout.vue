<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title> Stack game </q-toolbar-title>

        <div>Logged in as: <span class="text-bold">{{ idStore.username }}</span></div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-scroll-area class="fit"
        ><game-manager-vue></game-manager-vue
      ></q-scroll-area>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import GameManagerVue from 'src/components/GameManager.vue';
import { mapStores } from 'pinia';
import { useIdentityStore } from 'src/stores/id-store';

export default defineComponent({
  name: 'MainLayout',

  components: {
    GameManagerVue
  },
  computed: {
    ...mapStores(useIdentityStore)
  },
  data() {
    return {
      leftDrawerOpen: false
    };
  },

  methods: {
    toggleLeftDrawer() {
      this.leftDrawerOpen = !this.leftDrawerOpen;
    }
  }
});
</script>
