<template>
  <div class="fixed-top z-top bg-white">
    <q-btn-group spread outline class="q-ma-xs">
      <q-btn label="New game" color="primary" @click="createNewGame" />
      <q-btn icon="update" color="primary" @click="refreshGames()" />
    </q-btn-group>
  </div>

  <q-list bordered separator Style="padding-top:44px">
    <q-item
      clickable
      v-ripple
      v-for="game in games"
      @click="(e) => goToGame(game.game_id)"
      :key="game.game_id"
    >
      <q-item-section>
        <q-item-label>{{ game.host }}'s Game</q-item-label>
        <q-item-label caption>{{
          `Size: ${game.height}X${game.width} | Target: ${game.line_target}`
        }}</q-item-label>
      </q-item-section>
    </q-item>
    <q-inner-loading :showing="gamesLoading"></q-inner-loading>
  </q-list>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { getGames, createNewGame } from 'src/api';
import { Game } from 'src/api/models';
export default defineComponent({
  data() {
    return {
      games: [] as Game[],
      gamesLoading: true
    };
  },
  mounted() {
    this.refreshGames();
  },
  methods: {
    goToGame(id?: number) {
      this.$router.push(`/games/${id}`);
    },
    refreshGames() {
      this.gamesLoading = true;
      getGames()
        .then((games) => {
          this.games = games;
        })
        .finally(() => {
          this.gamesLoading = false;
        });
    },
    createNewGame() {
      createNewGame(7, 7, 4).then((game) => {
        console.log(game);
        this.refreshGames();
      });
    }
  }
});
</script>

<style></style>
