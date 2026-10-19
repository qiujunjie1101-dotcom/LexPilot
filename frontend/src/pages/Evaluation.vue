<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  FlaskConical,
  Play,
  RefreshCw,
  ShieldCheck,
  XCircle,
} from 'lucide-vue-next';
import { api } from '@/api/client';
import Card from '@/components/ui/card/Card.vue';
import CardContent from '@/components/ui/card/CardContent.vue';
import CardHeader from '@/components/ui/card/CardHeader.vue';
import CardTitle from '@/components/ui/card/CardTitle.vue';
import CardDescription from '@/components/ui/card/CardDescription.vue';
import Button from '@/components/ui/button/Button.vue';
import Alert from '@/components/ui/alert/Alert.vue';
import Badge from '@/components/ui/badge/Badge.vue';
import Progress from '@/components/ui/progress/Progress.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import Dialog from '@/components/ui/dialog/Dialog.vue';
import StatCard from '@/components/business/StatCard.vue';
import RiskBadge from '@/components/business/RiskBadge.vue';
import Table from '@/components/ui/table/Table.vue';
import TableHeader from '@/components/ui/table/TableHeader.vue';
import TableBody from '@/components/ui/table/TableBody.vue';
import TableRow from '@/components/ui/table/TableRow.vue';
import TableHead from '@/components/ui/table/TableHead.vue';
import TableCell from '@/components/ui/table/TableCell.vue';
import { useToast } from '@/composables/useToast';
import { formatDuration, formatTime, percent } from '@/lib/format';
import type { EvalCase, EvalResult, EvalResultRow } from '@/types/api';

const { pushToast } = useToast();

const cases = ref<EvalCase[]>([]);
const casesLoading = ref(true);
const result = ref<EvalResult | null>(null);
const running = ref(false);
const durationMs = ref<number | null>(null);
const errorMessage = ref('');
const detailOpen = ref(false);
const activeRow = ref<EvalResultRow | null>(null);

interface RunHistoryItem {
  at: string;
  passed: number;
  total: number;
  duration: number;
  result: EvalResult;
}

const history = ref<RunHistoryItem[]>([]);

async function loadCases() {
  casesLoading.value = true;
  errorMessage.value = '';
  try {
    cases.value = await api<EvalCase[]>('/api/eval/cases');
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '评测用例加载失败';
  } finally {
    casesLoading.value = false;
  }
}

onMounted(loadCases);

const passRate = computed(() => (result.value ? percent(result.value.passed, result.value.total) : 0));
const failedCount = computed(() => (result.value ? result.value.total - result.value.passed : 0));

const progressClass = computed(() => {
  if (passRate.value >= 90) return 'bg-emerald-500';
  if (passRate.value >= 70) return 'bg-amber-500';
  return 'bg-red-500';
});

async function run() {
  running.value = true;
  errorMessage.value = '';
  const started = performance.now();
  try {
    const response = await api<EvalResult>('/api/eval/run', { method: 'POST' });
    const elapsed = Math.round(performance.now() - started);
    result.value = response;
    durationMs.value = elapsed;
    history.value = [
      {
        at: new Date().toISOString(),
        passed: response.passed,
        total: response.total,
        duration: elapsed,
        result: response,
      },
      ...history.value,
    ].slice(0, 5);
    pushToast('回归测试完成', {
      description: `${response.passed}/${response.total} 通过 · 用时 ${formatDuration(elapsed)}`,
      variant: response.passed === response.total ? 'success' : 'warning',
    });
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '回归测试执行失败';
    pushToast('回归测试失败', { description: errorMessage.value, variant: 'error' });
  } finally {
    running.value = false;
  }
}

function openRow(row: EvalResultRow) {
  activeRow.value = row;
  detailOpen.value = true;
}

function restoreRun(item: RunHistoryItem) {
  result.value = item.result;
  durationMs.value = item.duration;
}
</script>

<template>
  <div class="space-y-4">
    <Alert v-if="errorMessage" variant="destructive" title="评测未完成">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span>{{ errorMessage }}</span>
        <Button size="sm" variant="outline" @click="loadCases">重新加载用例</Button>
      </div>
    </Alert>

    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-muted-foreground">
        <span class="flex items-center gap-1.5"><FlaskConical class="h-3.5 w-3.5" />Golden Dataset <span class="font-medium text-foreground">{{ cases.length }}</span> 个用例</span>
        <span class="flex items-center gap-1.5"><ShieldCheck class="h-3.5 w-3.5" />覆盖风险等级、人工复核与增量审查</span>
      </div>
      <Button :loading="running" :disabled="running" @click="run">
        <Play v-if="!running" class="h-4 w-4" />
        运行回归测试
      </Button>
    </div>

    <div class="grid gap-3 sm:grid-cols-3">
      <StatCard
        title="通过率"
        :value="result ? `${passRate}%` : '—'"
        description="本轮断言通过比例"
        :icon="CheckCircle2"
        tone="emerald"
        :loading="running"
      />
      <StatCard
        title="通过 / 总数"
        :value="result ? `${result.passed} / ${result.total}` : '—'"
        :description="result ? `${failedCount} 个用例未通过` : '尚未运行评测'"
        :icon="ClipboardCheck"
        tone="sky"
        :loading="running"
      />
      <StatCard
        title="运行耗时"
        :value="durationMs !== null ? formatDuration(durationMs) : '—'"
        description="本次回归执行耗时"
        :icon="Clock3"
        tone="amber"
        :loading="running"
      />
    </div>

    <div class="grid gap-4 xl:grid-cols-3">
      <div class="space-y-4 xl:col-span-2">
        <Card v-if="running">
          <CardContent class="space-y-3 pt-5">
            <div class="flex items-center gap-2 text-xs text-muted-foreground">
              <RefreshCw class="h-3.5 w-3.5 animate-spin" />
              正在执行 Golden Dataset 回归测试…
            </div>
            <Skeleton v-for="index in 5" :key="index" class="h-10 w-full" />
          </CardContent>
        </Card>

        <template v-else-if="result">
          <Card>
            <div class="flex flex-wrap items-center justify-between gap-3 border-b border-border px-5 py-4">
              <div class="space-y-1">
                <h3 class="text-[15px] font-semibold">回归结果</h3>
                <p class="text-[11px] text-muted-foreground">逐用例比对风险等级、人工复核与必需命中规则</p>
              </div>
              <div class="flex items-center gap-2">
                <Badge
                  :class="
                    result.passed === result.total
                      ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300'
                      : 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300'
                  "
                >
                  {{ result.passed === result.total ? '全部通过' : `${failedCount} 个失败` }}
                </Badge>
                <span class="text-sm font-semibold tabular-nums">{{ result.passed }}/{{ result.total }}</span>
              </div>
            </div>
            <div class="px-5 py-3">
              <Progress :value="passRate" :indicator-class="progressClass" />
            </div>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead class="w-[90px]">用例</TableHead>
                  <TableHead>合同</TableHead>
                  <TableHead class="w-[110px]">预期风险</TableHead>
                  <TableHead class="w-[110px]">实际风险</TableHead>
                  <TableHead class="w-[130px]">人工复核</TableHead>
                  <TableHead class="w-[100px]">结果</TableHead>
                  <TableHead class="w-[70px] text-right">详情</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow
                  v-for="row in result.results"
                  :key="row.id"
                  :class="!row.passed ? 'bg-red-50/40 dark:bg-red-500/[0.04]' : ''"
                >
                  <TableCell class="font-mono text-[11px]">{{ row.id }}</TableCell>
                  <TableCell>
                    <p class="font-mono text-[11px]">{{ row.contract_id }}</p>
                    <p v-if="row.expected.required_issue" class="mt-0.5 text-[10px] text-muted-foreground">
                      必需规则 {{ row.expected.required_issue }}
                    </p>
                  </TableCell>
                  <TableCell><RiskBadge :level="row.expected.expected_level" /></TableCell>
                  <TableCell><RiskBadge :level="row.actual.risk_level" /></TableCell>
                  <TableCell>
                    <span class="text-[11px] text-muted-foreground">
                      {{ row.expected.expected_legal ? '需要' : '不需要' }} / {{ row.actual.legal_review_required ? '已触发' : '未触发' }}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge
                      :class="
                        row.passed
                          ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300'
                          : 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300'
                      "
                    >
                      <CheckCircle2 v-if="row.passed" class="h-3 w-3" />
                      <XCircle v-else class="h-3 w-3" />
                      {{ row.passed ? 'PASS' : 'FAIL' }}
                    </Badge>
                  </TableCell>
                  <TableCell class="text-right">
                    <Button variant="ghost" size="xs" @click="openRow(row)">查看</Button>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </Card>
        </template>

        <Card v-else>
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-border px-5 py-4">
            <div class="space-y-1">
              <CardTitle>测试用例</CardTitle>
              <CardDescription>运行前可先核对 Golden Dataset 的预期结论</CardDescription>
            </div>
            <Button size="sm" :disabled="casesLoading || running" @click="run">
              <Play class="h-3.5 w-3.5" />
              开始评测
            </Button>
          </div>
          <div v-if="casesLoading" class="space-y-2 p-5">
            <Skeleton v-for="index in 5" :key="index" class="h-10 w-full" />
          </div>
          <EmptyState v-else-if="!cases.length" title="暂无用例" description="请检查后端 Golden Dataset 配置。" />
          <Table v-else>
            <TableHeader>
              <TableRow>
                <TableHead class="w-[90px]">用例</TableHead>
                <TableHead>合同</TableHead>
                <TableHead class="w-[110px]">预期风险</TableHead>
                <TableHead class="w-[110px]">人工复核</TableHead>
                <TableHead>断言条件</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="item in cases" :key="item.id">
                <TableCell class="font-mono text-[11px]">{{ item.id }}</TableCell>
                <TableCell class="font-mono text-[11px]">{{ item.contract_id }}</TableCell>
                <TableCell><RiskBadge :level="item.expected_level" /></TableCell>
                <TableCell class="text-[11px] text-muted-foreground">{{ item.expected_legal ? '需要' : '不需要' }}</TableCell>
                <TableCell class="whitespace-normal text-[11px] text-muted-foreground">
                  <span v-if="item.required_issue">命中 {{ item.required_issue }}</span>
                  <span v-else>无强制规则</span>
                  <span v-if="item.expected_changed_only?.length" class="ml-1">· 仅审查 {{ item.expected_changed_only.join(', ') }}</span>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </Card>
      </div>

      <div class="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>本次会话运行记录</CardTitle>
            <CardDescription>仅记录当前页面会话中的真实执行结果</CardDescription>
          </CardHeader>
          <CardContent>
            <div v-if="history.length" class="space-y-2">
              <button
                v-for="(item, index) in history"
                :key="item.at"
                type="button"
                :class="[
                  'w-full rounded-lg border px-3 py-2.5 text-left transition-colors',
                  result === item.result ? 'border-primary/30 bg-primary/[0.04]' : 'border-border hover:bg-muted/30',
                ]"
                @click="restoreRun(item)"
              >
                <div class="flex items-center justify-between gap-2">
                  <span class="text-xs font-medium">第 {{ history.length - index }} 次运行</span>
                  <span
                    :class="[
                      'text-xs font-semibold tabular-nums',
                      item.passed === item.total ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400',
                    ]"
                  >
                    {{ item.passed }}/{{ item.total }}
                  </span>
                </div>
                <div class="mt-1 flex items-center justify-between text-[10px] text-muted-foreground">
                  <span>{{ formatTime(item.at) }}</span>
                  <span>{{ formatDuration(item.duration) }}</span>
                </div>
              </button>
            </div>
            <EmptyState v-else compact title="尚未运行评测" description="运行一次回归后，这里会记录真实结果。" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>评测口径</CardTitle>
            <CardDescription>与后端断言逻辑保持一致</CardDescription>
          </CardHeader>
          <CardContent class="space-y-3 text-[11px] leading-5 text-muted-foreground">
            <div class="flex gap-2">
              <CheckCircle2 class="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
              <p>风险等级必须与预期完全一致。</p>
            </div>
            <div class="flex gap-2">
              <CheckCircle2 class="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
              <p>人工复核触发结果必须与预期一致。</p>
            </div>
            <div class="flex gap-2">
              <CheckCircle2 class="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
              <p>声明了必需规则的用例，必须实际命中对应 rule_id。</p>
            </div>
            <div class="flex gap-2">
              <CheckCircle2 class="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
              <p>增量审查用例的已审查条款范围必须与预期一致。</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <Dialog v-model:open="detailOpen" :title="activeRow ? `用例详情 · ${activeRow.id}` : '用例详情'" width="max-w-2xl">
      <div v-if="activeRow" class="space-y-3">
        <div class="flex flex-wrap items-center gap-2">
          <Badge
            :class="
              activeRow.passed
                ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300'
                : 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300'
            "
          >
            {{ activeRow.passed ? 'PASS' : 'FAIL' }}
          </Badge>
          <span class="font-mono text-[11px] text-muted-foreground">{{ activeRow.contract_id }}</span>
        </div>
        <div class="grid gap-3 sm:grid-cols-2">
          <div>
            <p class="mb-1.5 text-[11px] font-medium text-muted-foreground">预期断言</p>
            <pre class="mono">{{ JSON.stringify(activeRow.expected, null, 2) }}</pre>
          </div>
          <div>
            <p class="mb-1.5 text-[11px] font-medium text-muted-foreground">实际结果</p>
            <pre class="mono">{{ JSON.stringify(activeRow.actual, null, 2) }}</pre>
          </div>
        </div>
      </div>
      <template #footer>
        <Button variant="outline" @click="detailOpen = false">关闭</Button>
      </template>
    </Dialog>
  </div>
</template>
