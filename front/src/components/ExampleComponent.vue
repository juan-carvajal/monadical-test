<template>
  <div class="text-center text-h5">
    <p>There is no selected game!</p>
    <p>Pick one or create a new one from the left drawer</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import { Todo, Meta } from './models';

export default defineComponent({
  name: 'ExampleComponent',
  props: {
    title: {
      type: String,
      required: true
    },
    todos: {
      type: Array as PropType<Todo[]>,
      default: () => [] as Todo[]
    },
    meta: {
      type: Object as PropType<Meta>,
      required: true
    },
    active: {
      type: Boolean
    }
  },
  data(): { clickCount: number } {
    return {
      clickCount: 0
    };
  },
  methods: {
    increment (): void {
      this.clickCount += 1;
    }
  },
  computed: {
    todoCount (): number {
      return this.todos.length;
    }
  }
});
</script>
