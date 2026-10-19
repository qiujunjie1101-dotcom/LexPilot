<script setup lang="ts">
withDefaults(defineProps<{ value?: number; indicatorClass?: string }>(), {
  value: 0,
  indicatorClass: 'bg-primary',
});
</script>

<template>
  <div class="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
    <div
      class="h-full rounded-full transition-all duration-300"
      :class="indicatorClass"
      :style="{ width: `${Math.min(100, Math.max(0, value))}%` }"
    />
  </div>
</template>
