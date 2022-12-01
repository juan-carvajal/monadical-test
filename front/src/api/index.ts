import { useIdentityStore } from 'src/stores/id-store';
import axios from 'axios'
import { Game, GameStreamData, PlayerMove } from './models';

const identityStore = useIdentityStore()

const BACKEND_PATH = 'http://localhost:8000'


function getSessionToken () {
  return identityStore.username
}

export const getGames = () => {
  return axios.get(`${BACKEND_PATH}/games`, {
    params: {
      token: getSessionToken()
    }
  }).then(resp => {
    return resp.data as Game[]
  })
}

export const getGame = (id: number) => {
  return axios.get(`${BACKEND_PATH}/games/${id}`, {
    params: {
      token: getSessionToken()
    }
  }).then(resp => {
    return resp.data as Game
  })
}

export const makeMove = (gameId: number, move: PlayerMove) => {
  return axios.post(`${BACKEND_PATH}/games/${gameId}/moves`, move, {
    params: {
      token: getSessionToken()
    }
  }).then(resp => {
    return resp.data as GameStreamData
  })
}

export const joinGame = (gameId: number) => {
  return axios.post(`${BACKEND_PATH}/games/${gameId}/membership`, {}, {
    params: {
      token: getSessionToken()
    }
  }).then(resp => {
    return resp.data as Game
  })
}

export const createNewGame = (width: number, height: number, line_target: number) => {
  return axios.post(`${BACKEND_PATH}/games`, {
    width,
    height,
    line_target
  }, {
    params: {
      token: getSessionToken()
    }
  }).then(resp => {
    return resp.data as Game
  })
}
