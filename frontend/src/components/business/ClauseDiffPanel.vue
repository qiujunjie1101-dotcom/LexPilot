<script setup lang="ts">
import { computed } from 'vue';
import { AlertTriangle, ArrowRight } from 'lucide-vue-next';
import RiskBadge from '@/components/business/RiskBadge.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import { clauseTypeLabel, fieldLabel, formatDiffValue, formatFieldValue, parseDiffChange } from '@/lib/domain';
import type { ClauseDiff, ReviewIssue } from '@/types/api';

const props = defineProps<{
  diffs: ClauseDiff[];
  issues?: ReviewIssue[];
}>();

interface DiffField {
  key: string;
  label: string;
  standard: string;
  actual: string;
  changed: boolean;
}

interface DiffView extends ClauseDiff {
  fields: DiffField[];
  changeItems: { key: string; from: string; to: string }[];
  clauseIssues: ReviewIssue[];
}

const views = computed<DiffView[]>(() =>
  props.diffs.map((diff) => {
    const keys = Array.from(new Set([...Object.keys(diff.standard || {}), ...Object.keys(diff.actual || {})]));
    const changedKeys = new Set(
      diff.changes.map((change) => {
        const index = change.indexOf(':');
        return index > -1 ? change.slice(0, index) : change;
      }),
    );
    const fields = keys.map((key) => {
      const standard = formatFieldValue(key, diff.standard?.[key]);
      const actual = formatFieldValue(key, diff.actual?.[key]);
      return {
        key,
        label: fieldLabel(key),
        standard,
        actual,
        changed: changedKeys.has(key) || standard !== actual,
      };
    });
    return {
      ...diff,
      fields,
      changeItems: diff.changes.map(parseDiffChange),
      clauseIssues: (props.issues || []).filter((issue) => issue.clause_type === diff.clause_type),
    };
  }),
);
</script>

<template>
  <EmptyState v-if="!views.length" title="暂无条款差异" description="完成一次审查后，这里会展示标准条款与合同实际条款的逐字段差异。" />

  <div v-else class="space-y-4">
    <section v-for="view in views" :key="view.clause_type" class="overflow-hidden rounded-lg border border-border bg-card">
      <header class="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-muted/30 px-4 py-3">
        <div class="flex items-center gap-2">
          <span class="rounded-md border border-border bg-card px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
            {{ clauseTypeLabel(view.clause_type) }}
          </span>
          <h3 class="text-sm font-semibold">{{ view.title || clauseTypeLabel(view.clause_type) }}</h3>
        </div>
        <div class="flex items-center gap-1.5">
          <span
            :class="[
              'rounded-md px-2 py-0.5 text-[11px] font-medium',
              view.changes.length
                ? 'bg-amber-500/10 text-amber-700 dark:text-amber-400'
                : 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
            ]"
          >
            {{ view.changes.length ? `${view.changes.length} 处差异` : '与标准一致' }}
          </span>
        </div>
      </header>

      <div class="grid divide-y divide-border md:grid-cols-2 md:divide-x md:divide-y-0">
        <div class="p-4">
          <p class="mb-3 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">公司标准条款</p>
          <dl class="space-y-2.5">
            <div v-for="field in view.fields" :key="`std-${field.key}`" class="flex items-baseline justify-between gap-3 text-xs">
              <dt class="shrink-0 text-muted-foreground">{{ field.label }}</dt>
              <dd class="text-right font-medium text-foreground">{{ field.standard }}</dd>
            </div>
          </dl>
        </div>
        <div class="bg-muted/10 p-4">
          <p class="mb-3 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">客户合同条款</p>
          <dl class="space-y-2.5">
            <div v-for="field in view.fields" :key="`act-${field.key}`" class="flex items-baseline justify-between gap-3 text-xs">
              <dt class="shrink-0 text-muted-foreground">{{ field.label }}</dt>
              <dd
                :class="[
                  'rounded px-1.5 py-0.5 text-right font-medium',
                  field.changed
                    ? 'bg-amber-500/10 text-amber-700 ring-1 ring-amber-500/20 dark:text-amber-400'
                    : 'text-foreground',
                ]"
              >
                {{ field.actual }}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <div v-if="view.changeItems.length" class="border-t border-border px-4 py-3">
        <p class="mb-2 text-[11px] font-medium text-muted-foreground">差异明细</p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(item, index) in view.changeItems"
            :key="`${item.key}-${index}`"
            class="inline-flex items-center gap-1.5 rounded-md border border-border bg-muted/40 px-2 py-1 text-[11px]"
          >
            <span class="text-muted-foreground">{{ item.key }}</span>
            <span class="text-muted-foreground/70 line-through">{{ item.from }}</span>
            <ArrowRight class="h-3 w-3 text-muted-foreground" />
            <span class="font-medium text-foreground">{{ item.to }}</span>
          </span>
        </div>
      </div>

      <div v-if="view.clauseIssues.length" class="border-t border-border bg-red-50/40 px-4 py-3 dark:bg-red-500/5">
        <p class="mb-2 flex items-center gap-1.5 text-[11px] font-medium text-red-700 dark:text-red-400">
          <AlertTriangle class="h-3.5 w-3.5" />
          该条款命中 {{ view.clauseIssues.length }} 条风险规则
        </p>
        <ul class="space-y-2">
          <li v-for="issue in view.clauseIssues" :key="issue.rule_id" class="rounded-md border border-border bg-card px-3 py-2.5">
            <div class="flex flex-wrap items-center gap-2">
              <RiskBadge :level="issue.severity" />
              <span class="font-mono text-[10px] text-muted-foreground">{{ issue.rule_id }}</span>
            </div>
            <p class="mt-1.5 text-xs leading-5 text-foreground">{{ issue.reason }}</p>
            <p class="mt-1 text-xs leading-5 text-muted-foreground">
              <span class="font-medium text-foreground">修改建议：</span>{{ issue.suggestion }}
            </p>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>
