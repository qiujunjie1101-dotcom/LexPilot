<script setup lang="ts">
import { computed, onMounted, ref, type Component } from 'vue';
import type { EChartsOption } from 'echarts';
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ChevronRight,
  Clock3,
  FileSearch,
  FileText,
  ShieldAlert,
  UserCheck,
} from 'lucide-vue-next';
import { api } from '@/api/client';
import Card from '@/components/ui/card/Card.vue';
import CardContent from '@/components/ui/card/CardContent.vue';
import CardHeader from '@/components/ui/card/CardHeader.vue';
import CardTitle from '@/components/ui/card/CardTitle.vue';
import CardDescription from '@/components/ui/card/CardDescription.vue';
import Button from '@/components/ui/button/Button.vue';
import Alert from '@/components/ui/alert/Alert.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import Progress from '@/components/ui/progress/Progress.vue';
import Table from '@/components/ui/table/Table.vue';
import TableHeader from '@/components/ui/table/TableHeader.vue';
import TableBody from '@/components/ui/table/TableBody.vue';
import TableRow from '@/components/ui/table/TableRow.vue';
import TableHead from '@/components/ui/table/TableHead.vue';
import TableCell from '@/components/ui/table/TableCell.vue';
import ChartPanel from '@/components/ChartPanel.vue';
import StatCard from '@/components/business/StatCard.vue';
import RiskBadge from '@/components/business/RiskBadge.vue';
import StatusBadge from '@/components/business/StatusBadge.vue';
import ReviewDetailDialog from '@/components/business/ReviewDetailDialog.vue';
import { useAppStore } from '@/store/app';
import { useTheme } from '@/composables/useTheme';
import { RISK_BAR_CLASSES, RISK_CHART_COLORS, RISK_LABELS, RISK_ORDER, contractTypeLabel } from '@/lib/domain';
import { formatDateTime, formatNumber, percent } from '@/lib/format';
import type { DashboardData, LegalReviewRecord, ReviewRecord } from '@/types/api';

const { role } = useAppStore();
const { theme } = useTheme();

const data = ref<DashboardData | null>(null);
const reviews = ref<ReviewRecord[]>([]);
const legalReviews = ref<LegalReviewRecord[]>([]);
const loading = ref(true);
const errorMessage = ref('');
const detailOpen = ref(false);
const selectedReview = ref<ReviewRecord | null>(null);

async function load() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const [dashboard, recentReviews] = await Promise.all([
      api<DashboardData>('/api/dashboard'),
      api<ReviewRecord[]>('/api/reviews'),
    ]);
    data.value = dashboard;
    reviews.value = recentReviews;
    if (role.value === 'legal') {
      try {
        legalReviews.value = await api<LegalReviewRecord[]>('/api/legal-reviews');
      } catch {
        legalReviews.value = [];
      }
    } else {
      legalReviews.value = [];
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '数据加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(load);

const highRiskReviews = computed(() =>
  reviews.value.filter((review) => review.risk_level === 'high' || review.risk_level === 'critical'),
);

const highRiskContracts = computed(() => {
  const unique = new Map<string, ReviewRecord>();
  highRiskReviews.value.forEach((review) => {
    if (!unique.has(review.contract_id)) unique.set(review.contract_id, review);
  });
  return Array.from(unique.values());
});

const rejectedCount = computed(() => reviews.value.filter((review) => review.status === 'legal_rejected').length);

const riskTotal = computed(() => RISK_ORDER.reduce((sum, level) => sum + (data.value?.risk_counts[level] || 0), 0));

const riskRows = computed(() =>
  RISK_ORDER.map((level) => ({
    level,
    label: RISK_LABELS[level],
    count: data.value?.risk_counts[level] || 0,
    ratio: percent(data.value?.risk_counts[level] || 0, riskTotal.value),
    color: RISK_CHART_COLORS[level],
    barClass: RISK_BAR_CLASSES[level],
  })),
);

const pendingLegalItems = computed(() => legalReviews.value.filter((item) => item.status === 'pending').slice(0, 3));

const recentReviews = computed(() => reviews.value.slice(0, 6));

const axisColor = computed(() => (theme.value === 'dark' ? '#94a3b8' : '#64748b'));
const splitColor = computed(() => (theme.value === 'dark' ? 'rgba(148,163,184,0.16)' : 'rgba(100,116,139,0.12)'));

const chartOption = computed<EChartsOption>(() => ({
  grid: { left: 8, right: 8, top: 24, bottom: 0, containLabel: true },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    backgroundColor: theme.value === 'dark' ? '#0f172a' : '#ffffff',
    borderColor: splitColor.value,
    textStyle: { color: axisColor.value, fontSize: 12 },
    formatter: (params: unknown) => {
      const list = params as { axisValue: string; value: number }[];
      const item = list?.[0];
      if (!item) return '';
      const ratio = percent(item.value, riskTotal.value);
      return `<div style="font-weight:600;margin-bottom:4px">${item.axisValue}</div>审查结果 ${item.value} 条 · 占比 ${ratio}%`;
    },
  },
  xAxis: {
    type: 'category',
    data: RISK_ORDER.map((level) => RISK_LABELS[level]),
    axisLine: { lineStyle: { color: splitColor.value } },
    axisTick: { show: false },
    axisLabel: { color: axisColor.value, fontSize: 11 },
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: axisColor.value, fontSize: 11 },
    splitLine: { lineStyle: { color: splitColor.value } },
  },
  series: [
    {
      type: 'bar',
      barWidth: '42%',
      data: RISK_ORDER.map((level) => ({
        value: data.value?.risk_counts[level] || 0,
        itemStyle: { color: RISK_CHART_COLORS[level], borderRadius: [6, 6, 0, 0] },
      })),
      label: { show: true, position: 'top', color: axisColor.value, fontSize: 11 },
    },
  ],
}));

interface DashboardTask {
  label: string;
  description: string;
  count: number;
  to: string;
  icon: Component;
  tone: string;
}

const tasks = computed<DashboardTask[]>(() => [
  {
    label: '待法务复核',
    description: '高风险合同需法务终审确认',
    count: data.value?.pending_legal_reviews || 0,
    to: '/human-review',
    icon: UserCheck,
    tone: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  },
  {
    label: '高风险待确认',
    description: '最近审查中判定为高风险或严重风险',
    count: highRiskContracts.value.length,
    to: '/contracts',
    icon: ShieldAlert,
    tone: 'bg-red-500/10 text-red-600 dark:text-red-400',
  },
  {
    label: '法务驳回待整改',
    description: '审核未通过，需业务调整后重新提交',
    count: rejectedCount.value,
    to: '/review',
    icon: AlertTriangle,
    tone: 'bg-sky-500/10 text-sky-600 dark:text-sky-400',
  },
]);

function openDetail(review: ReviewRecord) {
  selectedReview.value = review;
  detailOpen.value = true;
}
</script>

<template>
  <div class="space-y-4">
    <Alert v-if="errorMessage" variant="destructive" title="看板数据加载失败">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span>{{ errorMessage }}</span>
        <Button size="sm" variant="outline" @click="load">重新加载</Button>
      </div>
    </Alert>

    <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard
        title="合同总数"
        :value="formatNumber(data?.contracts)"
        description="已归档合同与客户版本"
        :icon="FileText"
        tone="primary"
        to="/contracts"
        :loading="loading"
      />
      <StatCard
        title="审查总次数"
        :value="formatNumber(data?.reviews)"
        description="AI 初审累计执行次数"
        :icon="FileSearch"
        tone="sky"
        to="/review"
        :loading="loading"
      />
      <StatCard
        title="待法务复核"
        :value="formatNumber(data?.pending_legal_reviews)"
        description="需法务终审的风险合同"
        :icon="UserCheck"
        tone="amber"
        to="/human-review"
        :loading="loading"
      />
      <StatCard
        title="高风险合同"
        :value="formatNumber(highRiskContracts.length)"
        description="最近审查结果去重统计"
        :icon="ShieldAlert"
        tone="red"
        to="/contracts"
        :loading="loading"
      />
    </div>

    <div class="grid gap-4 xl:grid-cols-3">
      <Card class="min-w-0 xl:col-span-2">
        <div class="flex flex-wrap items-start justify-between gap-3 p-5 pb-3">
          <div class="space-y-1">
            <CardTitle>风险分布</CardTitle>
            <CardDescription>基于全部审查结果的风险等级分布</CardDescription>
          </div>
          <span class="rounded-md border border-border bg-muted/40 px-2 py-1 text-[11px] text-muted-foreground">
            共 {{ formatNumber(riskTotal) }} 次审查
          </span>
        </div>
        <CardContent class="min-w-0">
          <Skeleton v-if="loading" class="h-[248px] w-full" />
          <ChartPanel v-else :option="chartOption" height="248px" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>风险等级占比</CardTitle>
          <CardDescription>快速识别高风险审查结果密度</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <template v-if="loading">
            <Skeleton v-for="index in 4" :key="index" class="h-10 w-full" />
          </template>
          <template v-else>
            <div v-for="row in riskRows" :key="row.level" class="space-y-1.5">
              <div class="flex items-center justify-between text-xs">
                <span class="flex items-center gap-1.5">
                  <span class="h-2 w-2 rounded-sm" :style="{ backgroundColor: row.color }" />
                  <span class="font-medium">{{ row.label }}</span>
                </span>
                <span class="tabular-nums text-muted-foreground">
                  {{ formatNumber(row.count) }} 条 · {{ row.ratio }}%
                </span>
              </div>
              <Progress :value="row.ratio" :indicator-class="row.barClass" />
            </div>
            <div v-if="!riskTotal" class="pt-1">
              <EmptyState compact title="暂无审查结果" description="发起一次合同审查后即可查看风险占比。" />
            </div>
            <div v-else class="flex items-center gap-2 rounded-md border border-border bg-muted/30 px-3 py-2 text-[11px] text-muted-foreground">
              <CheckCircle2 class="h-3.5 w-3.5 text-emerald-500" />
              高风险与严重风险会自动进入法务复核流程
            </div>
          </template>
        </CardContent>
      </Card>
    </div>

    <div class="grid gap-4 xl:grid-cols-3">
      <Card class="xl:col-span-2">
        <div class="flex flex-wrap items-center justify-between gap-3 p-5 pb-3">
          <div class="space-y-1">
            <CardTitle>最近审查记录</CardTitle>
            <CardDescription>按提交时间倒序展示最近 6 次审查</CardDescription>
          </div>
          <RouterLink
            to="/review"
            class="inline-flex h-8 items-center gap-1 rounded-md px-3 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          >
            审查工作台
            <ChevronRight class="h-3.5 w-3.5" />
          </RouterLink>
        </div>
        <div class="px-2 pb-2">
          <div v-if="loading" class="space-y-2 px-3 pb-2">
            <Skeleton v-for="index in 5" :key="index" class="h-11 w-full" />
          </div>
          <EmptyState
            v-else-if="!recentReviews.length"
            compact
            title="暂无审查记录"
            description="从合同审查页选择合同并执行 AI 初审。"
          >
            <template #action>
              <RouterLink to="/review">
                <Button size="sm">发起审查</Button>
              </RouterLink>
            </template>
          </EmptyState>
          <Table v-else>
            <TableHeader>
              <TableRow>
                <TableHead>合同</TableHead>
                <TableHead>类型</TableHead>
                <TableHead>提交时间</TableHead>
                <TableHead>状态</TableHead>
                <TableHead>风险等级</TableHead>
                <TableHead class="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="review in recentReviews" :key="review.id" class="cursor-pointer" @click="openDetail(review)">
                <TableCell>
                  <div class="min-w-0">
                    <p class="truncate text-[13px] font-medium">{{ review.summary?.title || review.contract_id }}</p>
                    <p class="mt-0.5 truncate text-[11px] text-muted-foreground">{{ review.contract_id }} · {{ review.id }}</p>
                  </div>
                </TableCell>
                <TableCell class="text-xs text-muted-foreground">
                  {{ contractTypeLabel(review.summary?.contract_type) }}
                </TableCell>
                <TableCell class="whitespace-nowrap text-xs text-muted-foreground">
                  {{ formatDateTime(review.created_at) }}
                </TableCell>
                <TableCell><StatusBadge :status="review.status" kind="review" /></TableCell>
                <TableCell><RiskBadge :level="review.risk_level" /></TableCell>
                <TableCell class="text-right">
                  <Button variant="ghost" size="xs" @click.stop="openDetail(review)">详情</Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </Card>

      <div class="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>待办事项</CardTitle>
            <CardDescription>需要跟进的法务与审查任务</CardDescription>
          </CardHeader>
          <CardContent class="space-y-2">
            <RouterLink
              v-for="task in tasks"
              :key="task.label"
              :to="task.to"
              class="group flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2.5 transition-colors hover:border-primary/30 hover:bg-muted/30"
            >
              <span :class="['flex h-8 w-8 shrink-0 items-center justify-center rounded-md', task.tone]">
                <component :is="task.icon" class="h-4 w-4" />
              </span>
              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between gap-2">
                  <p class="text-xs font-medium">{{ task.label }}</p>
                  <span class="text-sm font-semibold tabular-nums">{{ task.count }}</span>
                </div>
                <p class="mt-0.5 truncate text-[11px] text-muted-foreground">{{ task.description }}</p>
              </div>
              <ArrowRight class="h-3.5 w-3.5 shrink-0 text-muted-foreground/60 transition-transform group-hover:translate-x-0.5 group-hover:text-primary" />
            </RouterLink>
          </CardContent>
        </Card>

        <Card>
          <div class="flex items-center justify-between p-5 pb-3">
            <div class="space-y-1">
              <CardTitle>待法务复核</CardTitle>
              <CardDescription>法务角色的实时待办队列</CardDescription>
            </div>
            <Clock3 class="h-4 w-4 text-muted-foreground" />
          </div>
          <CardContent>
            <div v-if="role !== 'legal'" class="rounded-md border border-dashed border-border bg-muted/20 px-3 py-4 text-center text-[11px] leading-5 text-muted-foreground">
              当前为业务人员视角。<br />
              切换为「法务审核员」后可查看复核队列。
            </div>
            <div v-else-if="loading" class="space-y-2">
              <Skeleton class="h-12 w-full" />
              <Skeleton class="h-12 w-full" />
            </div>
            <div v-else-if="pendingLegalItems.length" class="space-y-2">
              <RouterLink
                v-for="item in pendingLegalItems"
                :key="item.id"
                to="/human-review"
                class="block rounded-md border border-border bg-card px-3 py-2.5 transition-colors hover:border-primary/30 hover:bg-muted/30"
              >
                <div class="flex items-start justify-between gap-2">
                  <p class="min-w-0 truncate text-xs font-medium">{{ item.title }}</p>
                  <RiskBadge :level="item.risk_level" />
                </div>
                <p class="mt-1 text-[11px] text-muted-foreground">{{ item.version }} · {{ formatDateTime(item.created_at) }}</p>
              </RouterLink>
              <RouterLink to="/human-review" class="flex items-center justify-center gap-1 pt-1 text-[11px] text-primary hover:underline">
                查看全部复核任务
                <ArrowRight class="h-3 w-3" />
              </RouterLink>
            </div>
            <EmptyState v-else compact title="复核队列已清空" description="当前没有待处理的人工复核任务。" />
          </CardContent>
        </Card>
      </div>
    </div>

    <ReviewDetailDialog v-model:open="detailOpen" :review="selectedReview" />
  </div>
</template>
