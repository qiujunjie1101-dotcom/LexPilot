<script setup lang="ts">
withDefaults(defineProps<{ colspan?: number | string }>(), { colspan: 1 });
</script>

<template>
  <td :colspan="colspan" class="px-3 py-3 align-middle">
    <slot />
  </td>
</template>
