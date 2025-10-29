import { defineStore } from 'pinia';

// 1. Definimos la interfaz del estado
interface CounterState {
  counter: number;
}

export const useCounterStore = defineStore('counter', {
  // 2. Tipamos el estado
  state: (): CounterState => ({
    counter: 0,
  }),
  getters: {
    // 3. Tipamos los getters
    doubleCount: (state: CounterState): number => state.counter * 2,
  },
  actions: {
    increment() {
      this.counter++;
    },
  },
});