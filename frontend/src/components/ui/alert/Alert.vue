<script setup lang="ts">
import { computed } from 'vue';
import { cn } from '@/lib/utils';

const props = withDefaults(
  defineProps<{
    variant?: 'default' | 'info' | 'success' | 'warning' | 'destructive';
    title?: string;
  }>(),
  { variant: 'default' },
);

const variantClass = computed(
  () =>
    ({
      default: 'border-border bg-card text-card-foreground',
      info: 'border-blue-200 bg-blue-50 text-blue-900 dark:border-blue-500/30 dark:bg-blue-500/10 dark:text-blue-200',
      success:
        'border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-200',
      warning:
        'border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-200',
      destructive: 'border-red-200 bg-red-50 text-red-900 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-200',
    })[props.variant],
);
</script>

<template>
  <div role="alert" :class="cn('relative w-full rounded-lg border px-4 py-3 text-sm', variantClass)">
    <p v-if="props.title" class="mb-1 font-medium leading-none">{{ props.title }}</p>
    <div v-if="$slots.default" class="leading-relaxed">
      <slot />
    </div>
  </div>
</template>
