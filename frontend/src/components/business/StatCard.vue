<script setup lang="ts">
import { computed, type Component } from 'vue';
import { RouterLink } from 'vue-router';
import { ArrowUpRight } from 'lucide-vue-next';
import Card from '@/components/ui/card/Card.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';

const props = withDefaults(
  defineProps<{
    title: string;
    value: string | number;
    description?: string;
    icon: Component;
    tone?: 'primary' | 'emerald' | 'amber' | 'red' | 'sky';
    to?: string;
    loading?: boolean;
  }>(),
  { tone: 'primary', loading: false },
);

const toneClass = computed(
  () =>
    ({
      primary: 'bg-primary/10 text-primary ring-primary/15',
      emerald: 'bg-emerald-500/10 text-emerald-600 ring-emerald-500/15 dark:text-emerald-400',
      amber: 'bg-amber-500/10 text-amber-600 ring-amber-500/15 dark:text-amber-400',
      red: 'bg-red-500/10 text-red-600 ring-red-500/15 dark:text-red-400',
      sky: 'bg-sky-500/10 text-sky-600 ring-sky-500/15 dark:text-sky-400',
    })[props.tone],
);
</script>

<template>
  <component :is="props.to ? RouterLink : 'div'" :to="props.to" class="group block focus-visible:outline-none">
    <Card class="h-full transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-card-hover">
      <div class="flex items-start justify-between gap-3 p-5">
        <div class="min-w-0 space-y-1.5">
          <p class="text-xs font-medium text-muted-foreground">{{ title }}</p>
          <Skeleton v-if="loading" class="h-8 w-20" />
          <p v-else class="text-[28px] font-semibold leading-8 tracking-tight tabular-nums">{{ value }}</p>
          <p v-if="description" class="truncate text-xs text-muted-foreground">{{ description }}</p>
        </div>
        <div class="flex flex-col items-end gap-2">
          <span :class="['flex h-9 w-9 items-center justify-center rounded-lg ring-1', toneClass]">
            <component :is="props.icon" class="h-[18px] w-[18px]" />
          </span>
          <ArrowUpRight
            v-if="props.to"
            class="h-3.5 w-3.5 text-muted-foreground/50 transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-primary"
          />
        </div>
      </div>
    </Card>
  </component>
</template>
