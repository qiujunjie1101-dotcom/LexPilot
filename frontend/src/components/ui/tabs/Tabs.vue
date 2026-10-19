<script setup lang="ts">
import { cn } from '@/lib/utils';

export interface TabItem {
  value: string;
  label: string;
  count?: number;
}

const props = defineProps<{
  modelValue: string;
  items: TabItem[];
  class?: string;
}>();

const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>();
</script>

<template>
  <div :class="cn('inline-flex flex-wrap items-center gap-1 rounded-lg border border-border bg-muted/50 p-1', props.class)">
    <button
      v-for="item in props.items"
      :key="item.value"
      type="button"
      :class="
        cn(
          'inline-flex h-7 items-center gap-1.5 rounded-md px-3 text-xs font-medium transition-all',
          props.modelValue === item.value
            ? 'bg-card text-foreground shadow-sm'
            : 'text-muted-foreground hover:text-foreground',
        )
      "
      @click="emit('update:modelValue', item.value)"
    >
      {{ item.label }}
      <span
        v-if="item.count !== undefined"
        :class="[
          'rounded px-1.5 py-0.5 text-[10px] leading-none',
          props.modelValue === item.value ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground',
        ]"
      >
        {{ item.count }}
      </span>
    </button>
  </div>
</template>
