<script setup lang="ts">
import { Inbox } from 'lucide-vue-next';

withDefaults(
  defineProps<{
    title?: string;
    description?: string;
    compact?: boolean;
  }>(),
  {
    title: '暂无数据',
    description: '',
    compact: false,
  },
);
</script>

<template>
  <div :class="['flex flex-col items-center justify-center text-center', compact ? 'gap-2 py-6' : 'gap-3 py-12']">
    <div :class="['flex items-center justify-center rounded-full border border-border bg-muted/60 text-muted-foreground', compact ? 'h-9 w-9' : 'h-12 w-12']">
      <slot name="icon">
        <Inbox :class="compact ? 'h-4 w-4' : 'h-5 w-5'" />
      </slot>
    </div>
    <div class="space-y-1">
      <p :class="['font-medium text-foreground', compact ? 'text-[13px]' : 'text-sm']">{{ title }}</p>
      <p v-if="description" class="mx-auto max-w-md text-xs leading-5 text-muted-foreground">{{ description }}</p>
    </div>
    <div v-if="$slots.action" class="mt-1">
      <slot name="action" />
    </div>
  </div>
</template>
