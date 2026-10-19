<script setup lang="ts">
import { computed } from 'vue';
import { ChevronLeft, ChevronRight } from 'lucide-vue-next';

const props = withDefaults(
  defineProps<{
    page: number;
    pageSize: number;
    total: number;
  }>(),
  { page: 1, pageSize: 10, total: 0 },
);

const emit = defineEmits<{ (e: 'update:page', value: number): void }>();

const pageCount = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)));

const pages = computed<(number | string)[]>(() => {
  const count = pageCount.value;
  const current = props.page;
  if (count <= 7) return Array.from({ length: count }, (_, index) => index + 1);
  if (current <= 4) return [1, 2, 3, 4, 5, '…', count];
  if (current >= count - 3) return [1, '…', count - 4, count - 3, count - 2, count - 1, count];
  return [1, '…', current - 1, current, current + 1, '…', count];
});

function go(next: number) {
  if (next < 1 || next > pageCount.value || next === props.page) return;
  emit('update:page', next);
}
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3">
    <p class="text-xs text-muted-foreground">
      共 <span class="font-medium text-foreground">{{ total }}</span> 条 · 第 {{ page }} / {{ pageCount }} 页
    </p>
    <div class="flex items-center gap-1">
      <button
        type="button"
        class="flex h-7 w-7 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:bg-accent hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
        :disabled="page <= 1"
        aria-label="上一页"
        @click="go(page - 1)"
      >
        <ChevronLeft class="h-3.5 w-3.5" />
      </button>
      <template v-for="(item, index) in pages" :key="`${item}-${index}`">
        <span v-if="item === '…'" class="flex h-7 w-7 items-center justify-center text-xs text-muted-foreground">…</span>
        <button
          v-else
          type="button"
          :class="[
            'flex h-7 min-w-7 items-center justify-center rounded-md px-2 text-xs transition-colors',
            item === page
              ? 'bg-primary text-primary-foreground'
              : 'text-muted-foreground hover:bg-accent hover:text-foreground',
          ]"
          @click="go(item as number)"
        >
          {{ item }}
        </button>
      </template>
      <button
        type="button"
        class="flex h-7 w-7 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:bg-accent hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
        :disabled="page >= pageCount"
        aria-label="下一页"
        @click="go(page + 1)"
      >
        <ChevronRight class="h-3.5 w-3.5" />
      </button>
    </div>
  </div>
</template>
