<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  AlertTriangle,
  Columns2,
  FileSearch,
  GitCompare,
  RefreshCw,
} from 'lucide-vue-next';
import { api } from '@/api/client';
import Card from '@/components/ui/card/Card.vue';
import CardContent from '@/components/ui/card/CardContent.vue';
import Button from '@/components/ui/button/Button.vue';
import Select from '@/components/ui/select/Select.vue';
import Alert from '@/components/ui/alert/Alert.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import Progress from '@/components/ui/progress/Progress.vue';
import RiskBadge from '@/components/business/RiskBadge.vue';
import ClauseDiffPanel from '@/components/business/ClauseDiffPanel.vue';
import { useToast } from '@/composables/useToast';
import {
  RISK_BAR_CLASSES,
  clauseTypeLabel,
  contractTypeLabel,
} from '@/lib/domain';
import type { Contract, ContractDetail, ReviewRunResult, StandardClause } from '@/types/api';

const route = useRoute();
const router = useRouter();
const { pushToast } = useToast();

const contracts = ref<Contract[]>([]);
const templates = ref<StandardClause[]>([]);
const selectedId = ref('');
const result = ref<ReviewRunResult | null>(null);
const detail = ref<ContractDetail | null>(null);
const loading = ref(true);
const generating = ref(false);
const errorMessage = ref('');

const selectedContract = computed(() => contracts.value.find((contract) => contract.id === selectedId.value) || null);

const contractOptions = computed(() =>
  contracts.value.map((contract) => ({
    value: contract.id,
    label: `${contract.title} · ${contract.version}`,
  })),
);

const scoreBarClass = computed(() => (result.value && RISK_BAR_CLASSES[result.value.risk_level]) || 'bg-primary');

const severityRank: Record<string, number> = { low: 1, medium: 2, high: 3, critical: 4 };

const textRows = computed(() => {
  if (!result.value) return [];
  return result.value.diffs.map((diff) => {
    const standard = templates.value.find(
      (item) => item.contract_type === result.value?.contract_type && item.clause_type === diff.clause_type,
    );
    const actual = detail.value?.clauses.find((clause) => clause.clause_type === diff.clause_type);
    const clauseIssues = (result.value?.issues || []).filter((issue) => issue.clause_type === diff.clause_type);
    const highest = clauseIssues.reduce(
      (current, issue) => (severityRank[issue.severity] > severityRank[current] ? issue.severity : current),
      'low',
    );
    return {
      ...diff,
      standardText: standard?.standard_text || '',
      standardVersion: standard?.version || '',
      actualText: actual?.content || '',
      issues: clauseIssues,
      highestRisk: clauseIssues.length ? highest : null,
    };
  });
});

async function load() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const [contractRows, templateRows] = await Promise.all([
      api<Contract[]>('/api/contracts'),
      api<StandardClause[]>('/api/templates'),
    ]);
    contracts.value = [...contractRows].sort((a, b) => b.created_at.localeCompare(a.created_at));
    templates.value = templateRows;
    const queryContract = typeof route.query.contract === 'string' ? route.query.contract : '';
    if (queryContract && contracts.value.some((contract) => contract.id === queryContract)) {
      selectedId.value = queryContract;
    } else if (!selectedId.value && contracts.value.length) {
      const versioned = contracts.value.find((contract) => contract.parent_contract_id);
      selectedId.value = versioned?.id || contracts.value[0].id;
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '基础数据加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(load);

watch(selectedId, (next, previous) => {
  if (previous && next !== previous) {
    result.value = null;
    detail.value = null;
  }
});

async function generate() {
  if (!selectedId.value) {
    pushToast('请选择需要比对的合同', { variant: 'warning' });
    return;
  }
  generating.value = true;
  errorMessage.value = '';
  try {
    const [review, contractDetail] = await Promise.all([
      api<ReviewRunResult>(`/api/contracts/${selectedId.value}/review`, { method: 'POST' }),
      api<ContractDetail>(`/api/contracts/${selectedId.value}`),
    ]);
    result.value = review;
    detail.value = contractDetail;
    pushToast('条款比对已生成', {
      description: `${review.diffs.length} 类条款 · ${review.issues.length} 条风险问题`,
      variant: review.risk_level === 'low' ? 'success' : 'warning',
    });
    router.replace({ query: { ...route.query, contract: selectedId.value } });
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '条款比对失败';
    pushToast('条款比对失败', { description: errorMessage.value, variant: 'error' });
  } finally {
    generating.value = false;
  }
}
</script>

<template>
  <div class="space-y-4">
    <Alert v-if="errorMessage" variant="destructive" title="操作未完成">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span>{{ errorMessage }}</span>
        <Button size="sm" variant="outline" @click="load">重新加载</Button>
      </div>
    </Alert>

    <Card>
      <div class="flex flex-col gap-3 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:items-center">
          <div class="min-w-0 flex-1 sm:max-w-md">
            <Skeleton v-if="loading" class="h-9 w-full" />
            <Select v-else v-model="selectedId" :options="contractOptions" />
          </div>
          <div v-if="selectedContract" class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted-foreground">
            <span class="rounded border border-border bg-muted/40 px-1.5 py-0.5">{{ contractTypeLabel(selectedContract.contract_type) }}</span>
            <span>{{ selectedContract.version }}</span>
            <span>{{ selectedContract.parent_contract_id ? `父版本 ${selectedContract.parent_contract_id}` : '无父版本 · 全量审查' }}</span>
          </div>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <Button variant="outline" size="sm" :disabled="loading" @click="load">
            <RefreshCw :class="['h-4 w-4', loading ? 'animate-spin' : '']" />
            刷新
          </Button>
          <Button size="sm" :loading="generating" :disabled="loading || !selectedId" @click="generate">
            <GitCompare v-if="!generating" class="h-4 w-4" />
            生成条款比对
          </Button>
        </div>
      </div>
    </Card>

    <template v-if="result">
      <Card class="overflow-hidden">
        <div class="grid gap-px bg-border sm:grid-cols-2 xl:grid-cols-4">
          <div class="bg-card p-4">
            <p class="text-[11px] text-muted-foreground">风险结论</p>
            <div class="mt-1.5 flex items-center gap-2">
              <RiskBadge :level="result.risk_level" />
              <span class="text-lg font-semibold tabular-nums">{{ result.risk_score }}<span class="text-xs font-normal text-muted-foreground"> / 100</span></span>
            </div>
            <Progress class="mt-2.5" :value="result.risk_score" :indicator-class="scoreBarClass" />
          </div>
          <div class="bg-card p-4">
            <p class="text-[11px] text-muted-foreground">审查模式</p>
            <div class="mt-1.5 flex items-center gap-2 text-sm font-medium">
              <Columns2 class="h-4 w-4 text-muted-foreground" />
              {{ result.incremental_review ? '增量比对' : '全量比对' }}
            </div>
            <p class="mt-1 text-[11px] text-muted-foreground">
              {{ result.incremental_review ? '仅审查父版本变更条款' : '逐条对比全部条款' }}
            </p>
          </div>
          <div class="bg-card p-4">
            <p class="text-[11px] text-muted-foreground">条款范围</p>
            <p class="mt-1.5 text-sm font-medium">{{ result.reviewed_clause_types.length }} 类已审查</p>
            <p class="mt-1 text-[11px] text-muted-foreground">{{ result.diffs.length }} 类生成差异 · {{ result.issues.length }} 条风险</p>
          </div>
          <div class="bg-card p-4">
            <p class="text-[11px] text-muted-foreground">比对批次</p>
            <p class="mt-1.5 text-sm font-medium">本次会话生成</p>
            <p class="mt-1 truncate font-mono text-[10px] text-muted-foreground">{{ result.trace_id }}</p>
          </div>
        </div>
        <div v-if="result.changed_clause_types.length" class="flex flex-wrap items-center gap-1.5 border-t border-border bg-muted/20 px-4 py-2.5">
          <span class="text-[11px] text-muted-foreground">变更条款：</span>
          <span
            v-for="clause in result.changed_clause_types"
            :key="clause"
            class="rounded bg-amber-500/10 px-1.5 py-0.5 text-[11px] text-amber-700 dark:text-amber-400"
          >
            {{ clauseTypeLabel(clause) }}
          </span>
        </div>
      </Card>

      <Card>
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-border px-5 py-3.5">
          <div class="space-y-0.5">
            <h3 class="text-[15px] font-semibold">条款原文对照</h3>
            <p class="text-[11px] text-muted-foreground">左侧为公司标准条款，右侧为客户合同条款</p>
          </div>
          <div class="flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <Columns2 class="h-3.5 w-3.5" />
            {{ textRows.length }} 组条款
          </div>
        </div>
        <div class="divide-y divide-border">
          <section v-for="row in textRows" :key="row.clause_type">
            <div class="flex flex-wrap items-center justify-between gap-2 bg-muted/20 px-4 py-2.5">
              <div class="flex items-center gap-2">
                <span class="rounded border border-border bg-card px-1.5 py-0.5 text-[10px] text-muted-foreground">
                  {{ clauseTypeLabel(row.clause_type) }}
                </span>
                <h4 class="text-xs font-semibold">{{ row.title || clauseTypeLabel(row.clause_type) }}</h4>
                <span
                  v-if="row.changes.length"
                  class="rounded bg-amber-500/10 px-1.5 py-0.5 text-[10px] text-amber-700 dark:text-amber-400"
                >
                  {{ row.changes.length }} 处差异
                </span>
              </div>
              <RiskBadge v-if="row.highestRisk" :level="row.highestRisk" />
            </div>
            <div class="grid divide-y divide-border md:grid-cols-2 md:divide-x md:divide-y-0">
              <div class="p-4">
                <p class="mb-2 flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
                  公司标准条款
                  <span v-if="row.standardVersion" class="rounded bg-muted px-1 py-0.5 text-[9px]">{{ row.standardVersion }}</span>
                </p>
                <p class="max-h-52 overflow-y-auto whitespace-pre-wrap text-xs leading-6 text-muted-foreground">
                  {{ row.standardText || '暂无标准原文，请参考法务手册中的审查口径。' }}
                </p>
              </div>
              <div class="bg-amber-50/20 p-4 dark:bg-amber-500/[0.03]">
                <p class="mb-2 flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
                  客户合同条款
                  <span v-if="detail?.version" class="rounded bg-muted px-1 py-0.5 text-[9px]">{{ detail.version }}</span>
                </p>
                <p class="max-h-52 overflow-y-auto whitespace-pre-wrap text-xs leading-6">{{ row.actualText || '该合同中未找到对应条款原文。' }}</p>
              </div>
            </div>
            <div v-if="row.issues.length" class="border-t border-border bg-red-50/30 px-4 py-3 dark:bg-red-500/[0.04]">
              <p class="mb-1.5 flex items-center gap-1.5 text-[11px] font-medium text-red-700 dark:text-red-400">
                <AlertTriangle class="h-3.5 w-3.5" />
                命中 {{ row.issues.length }} 条风险规则
              </p>
              <ul class="space-y-1">
                <li v-for="issue in row.issues" :key="issue.rule_id" class="text-[11px] leading-5 text-muted-foreground">
                  <span class="font-mono text-[10px]">{{ issue.rule_id }}</span> · {{ issue.reason }}
                </li>
              </ul>
            </div>
          </section>
        </div>
      </Card>

      <Card>
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-border px-5 py-3.5">
          <div class="space-y-0.5">
            <h3 class="text-[15px] font-semibold">字段级差异与风险</h3>
            <p class="text-[11px] text-muted-foreground">标准化字段逐项对照，差异值高亮显示</p>
          </div>
          <RiskBadge :level="result.risk_level" />
        </div>
        <div class="p-4">
          <ClauseDiffPanel :diffs="result.diffs" :issues="result.issues" />
        </div>
      </Card>
    </template>

    <Card v-else-if="generating">
      <CardContent class="space-y-3 pt-5">
        <Skeleton class="h-20 w-full" />
        <Skeleton class="h-32 w-full" />
        <Skeleton class="h-32 w-full" />
      </CardContent>
    </Card>

    <Card v-else>
      <CardContent class="pt-5">
        <EmptyState
          title="选择合同后生成条款比对"
          description="系统会对比公司标准条款与客户合同条款，标记字段差异、风险变化与修改建议。"
        >
          <template #icon><GitCompare class="h-5 w-5" /></template>
          <template #action>
            <Button :loading="generating" :disabled="loading || !selectedId" @click="generate">
              <FileSearch v-if="!generating" class="h-4 w-4" />
              生成条款比对
            </Button>
          </template>
        </EmptyState>
      </CardContent>
    </Card>
  </div>
</template>
