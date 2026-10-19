<script setup lang="ts">
import { computed } from 'vue';
import Badge from '@/components/ui/badge/Badge.vue';
import { statusBadgeClass, statusLabel, type StatusKind } from '@/lib/domain';

const props = withDefaults(
  defineProps<{
    status?: string | null;
    kind?: StatusKind;
    dot?: boolean;
  }>(),
  { kind: 'review', dot: true },
);

const badgeClass = computed(() => statusBadgeClass(props.status, props.kind));
const label = computed(() => statusLabel(props.status, props.kind));
</script>

<template>
  <Badge :class="badgeClass">
    <span v-if="dot" class="h-1.5 w-1.5 rounded-full bg-current opacity-80" />
    {{ label }}
  </Badge>
</template>
