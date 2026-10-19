<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { CalendarClock, GitBranch, ShieldAlert } from 'lucide-vue-next';
import Dialog from '@/components/ui/dialog/Dialog.vue';
import Button from '@/components/ui/button/Button.vue';
import RiskBadge from '@/components/business/RiskBadge.vue';
import StatusBadge from '@/components/business/StatusBadge.vue';
import Progress from '@/components/ui/progress/Progress.vue';
import { RISK_BAR_CLASSES, clauseTypeLabel } from '@/lib/domain';
import { formatDateTime } from '@/lib/format';
import type { ReviewRecord } from '@/types/api';

const props = defineProps<{
  open: boolean;
  review?: ReviewRecord | null;
}>();

const emit = defineEmits<{ (e: 'update:open', value: boolean): void }>();
const router = useRouter();

const summary = computed(() => props.review?.summary || null);
const issues = computed(() => summary.value?.issues || []);
const visibleIssues = computed(() => issues.value.slice(0, 6));
const indicatorClass = computed(() => (props.review && RISK_BAR_CLASSES[props.review.risk_level]) || 'bg-primary');

function goTrace() {
  if (!props.review?.trace_id) return;
  emit('update:open', false);
  router.push({ path: '/trace', query: { trace_id: props.review.trace_id } });
}
</script>

<template>
  <Dialog
    :open="props.open"
    title="审查详情"
    :description="props.review ? `${props.review.id} · ${props.review.contract_id}` : '查看审查结果与风险依据'"
    width="max-w-2xl"
    @update:open="emit('update:open', $event)"
  >
    <div v-if="props.review" class="space-y-4">
      <section class="rounded-lg border border-border">
        <div class="grid gap-px overflow-hidden rounded-lg bg-border sm:grid-cols-3">
          <div class="bg-card p-3.5">
            <p class="text-[11px] text-muted-foreground">风险等级</p>
            <div class="mt-1.5"><RiskBadge :level="props.review.risk_level" /></div>
          </div>
          <div class="bg-card p-3.5">
            <p class="text-[11px] text-muted-foreground">风险评分</p>
            <p class="mt-1 text-lg font-semibold tabular-nums">{{ props.review.risk_score }}<span class="ml-0.5 text-xs font-normal text-muted-foreground">/ 100</span></p>
            <Progress class="mt-2" :value="props.review.risk_score" :indicator-class="indicatorClass" />
          </div>
          <div class="bg-card p-3.5">
            <p class="text-[11px] text-muted-foreground">流转状态</p>
            <div class="mt-1.5"><StatusBadge :status="props.review.status" kind="review" /></div>
          </div>
        </div>
      </section>

      <section class="grid gap-2 text-xs sm:grid-cols-2">
        <div class="flex items-center gap-2 rounded-md border border-border bg-muted/30 px-3 py-2">
          <CalendarClock class="h-3.5 w-3.5 text-muted-foreground" />
          <span class="text-muted-foreground">提交时间</span>
          <span class="ml-auto font-medium">{{ formatDateTime(props.review.created_at) }}</span>
        </div>
        <div class="flex items-center gap-2 rounded-md border border-border bg-muted/30 px-3 py-2">
          <GitBranch class="h-3.5 w-3.5 text-muted-foreground" />
          <span class="text-muted-foreground">Trace ID</span>
          <span class="ml-auto truncate font-mono text-[10px]">{{ props.review.trace_id }}</span>
        </div>
      </section>

      <section>
        <div class="mb-2 flex items-center justify-between">
          <h3 class="flex items-center gap-1.5 text-[13px] font-semibold">
            <ShieldAlert class="h-4 w-4 text-muted-foreground" />
            风险问题
          </h3>
          <span class="text-[11px] text-muted-foreground">共 {{ issues.length }} 条</span>
        </div>
        <div v-if="visibleIssues.length" class="space-y-2">
          <article v-for="issue in visibleIssues" :key="issue.rule_id" class="rounded-md border border-border bg-card px-3 py-2.5">
            <div class="flex flex-wrap items-center gap-2">
              <RiskBadge :level="issue.severity" />
              <span class="text-[11px] font-medium">{{ clauseTypeLabel(issue.clause_type) }}</span>
              <span class="font-mono text-[10px] text-muted-foreground">{{ issue.rule_id }}</span>
            </div>
            <p class="mt-1.5 text-xs leading-5">{{ issue.reason }}</p>
            <p class="mt-1 text-xs leading-5 text-muted-foreground">建议：{{ issue.suggestion }}</p>
          </article>
          <p v-if="issues.length > visibleIssues.length" class="text-[11px] text-muted-foreground">
            另有 {{ issues.length - visibleIssues.length }} 条问题，请进入完整审查页查看。
          </p>
        </div>
        <div v-else class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-xs text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300">
          本次审查未命中风险规则。
        </div>
      </section>

      <section v-if="summary?.summary?.summary">
        <h3 class="mb-2 text-[13px] font-semibold">AI 审查摘要</h3>
        <div class="rounded-md border border-border bg-muted/30 p-3 text-xs leading-6 text-muted-foreground">
          {{ summary.summary.summary }}
        </div>
      </section>
    </div>

    <template #footer>
      <Button variant="outline" @click="emit('update:open', false)">关闭</Button>
      <Button :disabled="!props.review?.trace_id" @click="goTrace">
        <GitBranch class="h-4 w-4" />
        查看审查链路
      </Button>
    </template>
  </Dialog>
</template>
