<script setup lang="ts">
import { computed } from 'vue';
import Badge from '@/components/ui/badge/Badge.vue';
import { riskBadgeClass, riskLabel } from '@/lib/domain';

const props = withDefaults(defineProps<{ level?: string | null; dot?: boolean }>(), { dot: true });

const badgeClass = computed(() => riskBadgeClass(props.level));
const label = computed(() => riskLabel(props.level));
</script>

<template>
  <Badge :class="badgeClass">
    <span v-if="dot" class="h-1.5 w-1.5 rounded-full bg-current opacity-80" />
    {{ label }}
  </Badge>
</template>
