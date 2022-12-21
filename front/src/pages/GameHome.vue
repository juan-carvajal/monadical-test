<template>
  <q-page>
    <p class="text-h4 text-center">{{ turnMessage }}</p>
    <table v-if="gameState?.board">
      <tr v-for="(row, i) in gameState.board" :key="i">
        <td>
          <div class="content">
            <q-btn
              :disable="!canMove || isRowFull(row)"
              outline
              @click="makeMoveHandler(i, 'left')"
              class="fit"
              color="primary"
              icon="keyboard_double_arrow_right"
            ></q-btn>
          </div>
        </td>
        <td v-for="(cell, j) in row" :key="j">
          <div v-if="cell" class="content">
            <q-card class="fit">
              <div
                :class="`${
                  cell === idStore.username ? 'bg-primary' : 'bg-secondary'
                }`"
                style="border-radius: 50%"
                class="fit shadow-2"
              ></div>
            </q-card>
          </div>
          <div v-else class="content">
            <q-card class="fit"></q-card>
          </div>
        </td>
        <td>
          <div class="content">
            <q-btn
              :disable="!canMove || isRowFull(row)"
              outline
              @click="makeMoveHandler(i, 'right')"
              class="fit"
              color="primary"
              icon="keyboard_double_arrow_left"
            ></q-btn>
          </div>
        </td>
      </tr>
    </table>
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { getGame, joinGame, makeMove } from 'src/api';
import {
  Game,
  GameStreamData,
  GameStreamDataBoardRow,
  PlayerMove
} from 'src/api/models';
import { mapStores } from 'pinia';
import { useIdentityStore } from 'src/stores/id-store';

const WS_URL = 'ws://localhost:8000/ws';

export default defineComponent({
  props: {
    id: {
      required: true,
      type: Number
    }
  },
  computed: {
    ...mapStores(useIdentityStore),
    turnMessage(): string {
      if (this?.game?.host === this.idStore.username && !this.enemyConnected) {
        return 'Waiting for an opponent!';
      }

      if (this.gameState?.turn === this.idStore.username) {
        return 'Your turn, make your move';
      }

      return `It is ${this.gameState?.turn}'s turn`;
    },
    canMove(): boolean {
      return (
        this?.gameState?.turn === this.idStore.username && this.enemyConnected
      );
    }
  },
  data() {
    return {
      game: null as Game | null,
      gameState: null as GameStreamData | null,
      enemyConnected: false,
      ws: null as WebSocket | null
    };
  },
  watch: {
    id: {
      immediate: true,
      handler(value) {
        if (!value) {
          return;
        }

        this.refreshGame();
      }
    },
    game(value: Game) {
      if (value.enemy) {
        this.enemyConnected = true;
      }
    }
  },
  methods: {
    isRowFull(row: (string|null)[]){
      return row.every(i => !!i)
    },
    makeMoveHandler(row: number, direction: 'right' | 'left') {
      const move: PlayerMove = {
        row: row,
        direction: direction
      };

      makeMove(this.id, move).catch((e) => {
        console.log(e);
      });
    },
    handleWSClose() {
      console.log('ws closed');
    },
    createdDefaultGameStreamData(game: Game): GameStreamData {
      const board: GameStreamDataBoardRow[] = [];
      for (let i = 0; i < game.height; i++) {
        const row: GameStreamDataBoardRow = [];
        for (let j = 0; j < game.width; j++) {
          row.push(null);
        }
        board.push(row);
      }

      return {
        board: board,
        winner: undefined,
        turn: undefined
      };
    },
    handleWSError(error: any) {
      console.log(error);
      console.log('ws error');
      this.$router.push('/');
    },
    handleWSMessage(message: any) {
      console.log(message);
      const event = JSON.parse(message.data) as {
        type: string;
        payload: object;
      };

      if (event.type === 'opponent') {
        this.enemyConnected = true;
        return;
      }

      this.gameState = event.payload as GameStreamData;

      if (this.gameState.winner) {
        this.$q
          .dialog({
            title: 'Game Over!',
            message:
              this.gameState.winner === this.idStore.username
                ? 'You have won!'
                : 'Sorry, you lost this game.'
          })
          .onDismiss(() => {
            this.$router.push('/');
          });
      }
    },
    handleWSConnection() {
      this.ws = new WebSocket(
        `${WS_URL}/${this.id}?token=${this.idStore.username}`
      );
      this.ws.onclose = this.handleWSClose;
      this.ws.onmessage = this.handleWSMessage;
      this.ws.onerror = this.handleWSError;
    },
    refreshGame() {
      if (!this.id) {
        this.game = null;
      }

      getGame(this.id)
        .then((game) => {
          return game;
        })
        .then((game) => {
          if (
            game.host !== this.idStore.username &&
            game.enemy !== this.idStore.username
          ) {
            return joinGame(this.id);
          }

          return game;
        })
        .then((game) => {
          this.game = game;
          this.gameState = this.createdDefaultGameStreamData(game);
        })
        .then(() => {
          this.handleWSConnection();
        })
        .catch((e) => {
          console.log(e);
          this.game = null;
        });
    }
  }
});
</script>

<style scoped>
table {
  width: 50%;
  margin: auto;
}
td {
  position: relative;
}
td:after {
  content: '';
  display: block;
  margin-top: 100%;
}
td .content {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
}
</style>
