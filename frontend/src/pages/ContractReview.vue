<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  ArrowRight,
  Copy,
  FileSearch,
  FileUp,
  GitCompare,
  Layers,
  Loader2,
  Play,
  Scale,
  ShieldCheck,
  Sparkles,
} from 'lucide-vue-next';
import { api } from '@/api/client';
import Card from '@/components/ui/card/Card.vue';
import CardContent from '@/components/ui/card/CardContent.vue';
import Button from '@/components/ui/button/Button.vue';
import Select from '@/components/ui/select/Select.vue';
import Alert from '@/components/ui/alert/Alert.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import Tabs from '@/components/ui/tabs/Tabs.vue';
import Progress from '@/components/ui/progress/Progress.vue';
import Table from '@/components/ui/table/Table.vue';
import TableHeader from '@/components/ui/table/TableHeader.vue';
import TableBody from '@/components/ui/table/TableBody.vue';
import TableRow from '@/components/ui/table/TableRow.vue';
import TableHead from '@/components/ui/table/TableHead.vue';
import TableCell from '@/components/ui/table/TableCell.vue';
import RiskBadge from '@/components/business/RiskBadge.vue';
import StatusBadge from '@/components/business/StatusBadge.vue';
import ClauseDiffPanel from '@/components/business/ClauseDiffPanel.vue';
import ContractImportDialog from '@/components/business/ContractImportDialog.vue';
import { useToast } from '@/composables/useToast';
import {
  RISK_BAR_CLASSES,
  clauseTypeLabel,
  contractTypeLabel,
  riskLabel,
} from '@/lib/domain';
import { formatAmount } from '@/lib/format';
import type { Contract, ReviewRunResult } from '@/types/api';

const route = useRoute();
const router = useRouter();
const { pushToast } = useToast();

const contracts = ref<Contract[]>([]);
const selectedId = ref('');
const result = ref<ReviewRunResult | null>(null);
const loadingContracts = ref(true);
const running = ref(false);
const errorMessage = ref('');
const activeTab = ref('issues');
const importOpen = ref(false);

const selectedContract = computed(() => contracts.value.find((contract) => contract.id === selectedId.value) || null);

const contractOptions = computed(() =>
  contracts.value.map((contract) => ({
    value: contract.id,
    label: `${contract.title} · ${contract.version}`,
  })),
);

const tabItems = computed(() => [
  { value: 'issues', label: '风险问题', count: result.value?.issues.length || 0 },
  { value: 'diffs', label: '条款差异', count: result.value?.diffs.length || 0 },
  { value: 'evidence', label: '法务依据', count: result.value?.evidence.length || 0 },
  { value: 'summary', label: 'AI 摘要' },
]);

const scoreBarClass = computed(() => (result.value && RISK_BAR_CLASSES[result.value.risk_level]) || 'bg-primary');

async function loadContracts() {
  loadingContracts.value = true;
  try {
    const rows = await api<Contract[]>('/api/contracts');
    contracts.value = [...rows].sort((a, b) => b.created_at.localeCompare(a.created_at));
    const queryContract = typeof route.query.contract === 'string' ? route.query.contract : '';
    if (queryContract && contracts.value.some((contract) => contract.id === queryContract)) {
      selectedId.value = queryContract;
    } else if (!selectedId.value && contracts.value.length) {
      selectedId.value = contracts.value[0].id;
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '合同列表加载失败';
  } finally {
    loadingContracts.value = false;
  }
}

onMounted(loadContracts);

watch(selectedId, (next, previous) => {
  if (previous && next !== previous) {
    result.value = null;
    activeTab.value = 'issues';
  }
});

async function run() {
  if (!selectedId.value) {
    pushToast('请选择需要审查的合同', { variant: 'warning' });
    return;
  }
  running.value = true;
  errorMessage.value = '';
  try {
    result.value = await api<ReviewRunResult>(`/api/contracts/${selectedId.value}/review`, { method: 'POST' });
    activeTab.value = 'issues';
    pushToast(`审查完成 · ${riskLabel(result.value.risk_level)}`, {
      description: `风险评分 ${result.value.risk_score} 分，${result.value.issues.length} 条风险问题`,
      variant: result.value.risk_level === 'low' ? 'success' : 'warning',
    });
    router.replace({ query: { ...route.query, contract: selectedId.value } });
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '审查执行失败';
    pushToast('审查执行失败', { description: errorMessage.value, variant: 'error' });
  } finally {
    running.value = false;
  }
}

async function copyTrace() {
  if (!result.value?.trace_id) return;
  try {
    await navigator.clipboard.writeText(result.value.trace_id);
    pushToast('Trace ID 已复制', { variant: 'success' });
  } catch {
    pushToast('复制失败', { description: result.value.trace_id, variant: 'error' });
  }
}

function onImported(contract: Contract) {
  contracts.value = [contract, ...contracts.value];
  selectedId.value = contract.id;
}

function goTrace() {
  if (!result.value) return;
  router.push({ path: '/trace', query: { trace_id: result.value.trace_id } });
}

function goDiff() {
  if (!selectedId.value) return;
  router.push({ path: '/diff', query: { contract: selectedId.value } });
}
</script>

<template>
  <div class="space-y-4">
    <Alert v-if="errorMessage" variant="destructive" title="操作未完成">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span>{{ errorMessage }}</span>
        <Button size="sm" variant="outline" @click="loadContracts">刷新合同</Button>
      </div>
    </Alert>

    <Card>
      <div class="flex flex-col gap-3 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:items-center">
          <div class="min-w-0 flex-1 sm:max-w-md">
            <Skeleton v-if="loadingContracts" class="h-9 w-full" />
            <Select v-else v-model="selectedId" :options="contractOptions" />
          </div>
          <div v-if="selectedContract" class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted-foreground">
            <span class="rounded border border-border bg-muted/40 px-1.5 py-0.5">{{ contractTypeLabel(selectedContract.contract_type) }}</span>
            <span>{{ selectedContract.version }}</span>
            <span>{{ formatAmount(selectedContract.amount) }}</span>
            <span>{{ selectedContract.department_id }}</span>
          </div>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <Button variant="outline" size="sm" @click="importOpen = true">
            <FileUp class="h-4 w-4" />
            导入合同
          </Button>
          <Button size="sm" :loading="running" :disabled="loadingContracts || !selectedId" @click="run">
            <Play v-if="!running" class="h-4 w-4" />
            开始审查
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
              <Layers class="h-4 w-4 text-muted-foreground" />
              {{ result.incremental_review ? '增量审查' : '全量审查' }}
            </div>
            <p class="mt-1 text-[11px] text-muted-foreground">
              {{ result.incremental_review ? `父版本 ${result.parent_contract_id}` : '覆盖全部合同条款' }}
            </p>
          </div>
          <div class="bg-card p-4">
            <p class="text-[11px] text-muted-foreground">流转状态</p>
            <div class="mt-1.5"><StatusBadge :status="result.status" kind="review" /></div>
            <p class="mt-1 text-[11px] text-muted-foreground">
              {{ result.legal_review_required ? '已自动创建法务复核任务' : '无需人工复核，可继续推进' }}
            </p>
          </div>
          <div class="bg-card p-4">
            <p class="text-[11px] text-muted-foreground">审查编号</p>
            <p class="mt-1.5 font-mono text-xs font-medium">{{ result.review_id }}</p>
            <button type="button" class="mt-1 flex items-center gap-1 text-[11px] text-muted-foreground hover:text-primary" @click="copyTrace">
              <Copy class="h-3 w-3" />
              {{ result.trace_id }}
            </button>
          </div>
        </div>
        <div class="flex flex-wrap items-center justify-between gap-2 border-t border-border bg-muted/20 px-4 py-2.5">
          <div class="flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
            <span>已审查 {{ result.reviewed_clause_types.length }} 类条款</span>
            <span class="text-border">·</span>
            <span>变更 {{ result.changed_clause_types.length }} 类</span>
            <template v-if="result.changed_clause_types.length">
              <span
                v-for="clause in result.changed_clause_types"
                :key="clause"
                class="rounded bg-amber-500/10 px-1.5 py-0.5 text-amber-700 dark:text-amber-400"
              >
                {{ clauseTypeLabel(clause) }}
              </span>
            </template>
          </div>
          <div class="flex items-center gap-1.5">
            <Button variant="ghost" size="xs" @click="goDiff">
              <GitCompare class="h-3.5 w-3.5" />
              条款比对
            </Button>
            <Button variant="outline" size="xs" @click="goTrace">
              <ArrowRight class="h-3.5 w-3.5" />
              查看链路
            </Button>
          </div>
        </div>
      </Card>

      <div class="flex items-center justify-between gap-2">
        <Tabs v-model="activeTab" :items="tabItems" />
        <span class="hidden text-[11px] text-muted-foreground sm:block">{{ result.summary?.summary ? 'AI 摘要已生成' : '' }}</span>
      </div>

      <Card v-if="activeTab === 'issues'">
        <CardContent class="pt-5">
          <div v-if="result.issues.length" class="overflow-hidden rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead class="w-[90px]">严重程度</TableHead>
                  <TableHead class="w-[110px]">条款</TableHead>
                  <TableHead class="w-[150px]">规则</TableHead>
                  <TableHead>风险原因</TableHead>
                  <TableHead>修改建议</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="issue in result.issues" :key="issue.rule_id">
                  <TableCell><RiskBadge :level="issue.severity" /></TableCell>
                  <TableCell class="text-xs">{{ clauseTypeLabel(issue.clause_type) }}</TableCell>
                  <TableCell><span class="font-mono text-[10px] text-muted-foreground">{{ issue.rule_id }}</span></TableCell>
                  <TableCell class="max-w-[320px] whitespace-normal text-xs leading-5">{{ issue.reason }}</TableCell>
                  <TableCell class="max-w-[320px] whitespace-normal text-xs leading-5 text-muted-foreground">{{ issue.suggestion }}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
          <Alert v-else variant="success" title="未发现红线风险">
            本次审查未命中风险规则，仍建议人工确认商业条款与特殊约定。
          </Alert>
        </CardContent>
      </Card>

      <Card v-else-if="activeTab === 'diffs'">
        <CardContent class="pt-5">
          <ClauseDiffPanel :diffs="result.diffs" :issues="result.issues" />
        </CardContent>
      </Card>

      <Card v-else-if="activeTab === 'evidence'">
        <CardContent class="pt-5">
          <div v-if="result.evidence.length" class="overflow-hidden rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Playbook</TableHead>
                  <TableHead class="w-[70px]">版本</TableHead>
                  <TableHead class="w-[110px]">条款</TableHead>
                  <TableHead class="w-[80px]">相关度</TableHead>
                  <TableHead>审查口径</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="item in result.evidence" :key="item.id">
                  <TableCell class="min-w-[160px] text-xs font-medium">{{ item.title }}</TableCell>
                  <TableCell class="text-xs text-muted-foreground">{{ item.version }}</TableCell>
                  <TableCell class="text-xs">{{ clauseTypeLabel(item.clause_type) }}</TableCell>
                  <TableCell class="text-xs tabular-nums">{{ (item.rerank_score * 100).toFixed(0) }}%</TableCell>
                  <TableCell class="max-w-[420px] whitespace-normal text-xs leading-5 text-muted-foreground">{{ item.content }}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
          <EmptyState v-else title="暂无检索依据" description="本次审查未召回相关 Playbook 条款。" />
        </CardContent>
      </Card>

      <Card v-else>
        <CardContent class="space-y-4 pt-5">
          <section class="rounded-lg border border-border bg-muted/20 p-4">
            <div class="mb-1.5 flex items-center gap-1.5 text-xs font-semibold">
              <Sparkles class="h-4 w-4 text-primary" />
              AI 审查摘要
            </div>
            <p class="text-[13px] leading-6 text-muted-foreground">{{ result.summary?.summary || '暂无摘要' }}</p>
          </section>
          <section class="rounded-lg border border-border p-4">
            <div class="mb-1.5 flex items-center gap-1.5 text-xs font-semibold">
              <Scale class="h-4 w-4 text-muted-foreground" />
              业务建议
            </div>
            <p class="text-[13px] leading-6 text-muted-foreground">{{ result.summary?.business_advice || '暂无建议' }}</p>
          </section>
          <Alert v-if="result.summary?.disclaimer" variant="warning">{{ result.summary.disclaimer }}</Alert>
        </CardContent>
      </Card>
    </template>

    <Card v-else-if="!loadingContracts">
      <CardContent class="pt-5">
        <EmptyState
          v-if="!contracts.length"
          title="还没有可审查的合同"
          description="先导入一份合同，系统会解析条款结构并加入审查队列。"
        >
          <template #icon><FileSearch class="h-5 w-5" /></template>
          <template #action>
            <Button size="sm" @click="importOpen = true">
              <FileUp class="h-4 w-4" />
              导入第一份合同
            </Button>
          </template>
        </EmptyState>

        <div v-else class="mx-auto max-w-3xl py-4">
          <div class="mb-6 text-center">
            <div class="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <ShieldCheck class="h-[22px] w-[22px]" />
            </div>
            <h2 class="mt-3 text-base font-semibold">准备开始智能合同审查</h2>
            <p class="mt-1 text-xs leading-5 text-muted-foreground">
              选择合同后，Agent 会执行增量差异识别、红线规则校验与 Playbook 检索，并输出可执行修改建议。
            </p>
          </div>
          <div class="grid gap-3 sm:grid-cols-3">
            <div class="rounded-lg border border-border bg-muted/20 p-4">
              <span class="flex h-7 w-7 items-center justify-center rounded-md bg-card text-xs font-semibold text-primary shadow-sm">1</span>
              <p class="mt-2.5 text-xs font-medium">选择合同版本</p>
              <p class="mt-1 text-[11px] leading-5 text-muted-foreground">支持全量合同与客户修订版本。</p>
            </div>
            <div class="rounded-lg border border-border bg-muted/20 p-4">
              <span class="flex h-7 w-7 items-center justify-center rounded-md bg-card text-xs font-semibold text-primary shadow-sm">2</span>
              <p class="mt-2.5 text-xs font-medium">Agent 自动审查</p>
              <p class="mt-1 text-[11px] leading-5 text-muted-foreground">逐条款比对标准口径并检索法务手册。</p>
            </div>
            <div class="rounded-lg border border-border bg-muted/20 p-4">
              <span class="flex h-7 w-7 items-center justify-center rounded-md bg-card text-xs font-semibold text-primary shadow-sm">3</span>
              <p class="mt-2.5 text-xs font-medium">风险处置</p>
              <p class="mt-1 text-[11px] leading-5 text-muted-foreground">高风险自动进入法务复核并留痕。</p>
            </div>
          </div>
          <div class="mt-6 flex justify-center">
            <Button :loading="running" @click="run">
              <Loader2 v-if="running" class="h-4 w-4 animate-spin" />
              <Play v-else class="h-4 w-4" />
              对当前合同执行审查
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <div v-else class="grid gap-3 xl:grid-cols-3">
      <Skeleton class="h-24 w-full xl:col-span-2" />
      <Skeleton class="h-24 w-full" />
    </div>

    <ContractImportDialog v-model:open="importOpen" :contracts="contracts" @imported="onImported" />
  </div>
</template>
