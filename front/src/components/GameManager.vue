<template>
  <q-list bordered separator Style="">
    <div class="z-top bg-white">
      <q-btn-group spread outline class="q-ma-xs">
        <q-btn dense label="New game" color="primary" @click="createNewGame" />
        <q-btn
          dense
          label="New AI game"
          color="primary"
          @click="createAINewGameHandler"
        />
        <q-btn dense icon="update" color="primary" @click="refreshGames()" />
      </q-btn-group>
    </div>
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
  </q-list>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { getGames, createNewGame, createAINewGame } from 'src/api';
import { Game } from 'src/api/models';

const REFRESH_INTERVAL_IN_MS = 2500;
export default defineComponent({
  data() {
    return {
      games: [] as Game[],
      gamesLoading: true,
      refreshInterval: null as NodeJS.Timeout | null
    };
  },
  mounted() {
    this.refreshInterval = setInterval(
      this.refreshGames,
      REFRESH_INTERVAL_IN_MS
    );
  },
  unmounted() {
    if (!this.refreshInterval) {
      return;
    }

    clearInterval(this.refreshInterval);
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
    },
    createAINewGameHandler() {
      createAINewGame(7, 7, 4).then((game) => {
        console.log(game);
        this.refreshGames();
      });
    }
  }
});
</script>

<style></style>
