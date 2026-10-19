<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import {
  CalendarCheck2,
  CheckCircle2,
  ClipboardList,
  GitBranch,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  XCircle,
} from 'lucide-vue-next';
import { api } from '@/api/client';
import Card from '@/components/ui/card/Card.vue';
import Button from '@/components/ui/button/Button.vue';
import Input from '@/components/ui/input/Input.vue';
import Textarea from '@/components/ui/textarea/Textarea.vue';
import Alert from '@/components/ui/alert/Alert.vue';
import Skeleton from '@/components/ui/skeleton/Skeleton.vue';
import EmptyState from '@/components/ui/empty-state/EmptyState.vue';
import Tabs from '@/components/ui/tabs/Tabs.vue';
import Pagination from '@/components/ui/pagination/Pagination.vue';
import Dialog from '@/components/ui/dialog/Dialog.vue';
import StatCard from '@/components/business/StatCard.vue';
import RiskBadge from '@/components/business/RiskBadge.vue';
import StatusBadge from '@/components/business/StatusBadge.vue';
import Table from '@/components/ui/table/Table.vue';
import TableHeader from '@/components/ui/table/TableHeader.vue';
import TableBody from '@/components/ui/table/TableBody.vue';
import TableRow from '@/components/ui/table/TableRow.vue';
import TableHead from '@/components/ui/table/TableHead.vue';
import TableCell from '@/components/ui/table/TableCell.vue';
import { useAppStore } from '@/store/app';
import { useToast } from '@/composables/useToast';
import { formatDateTime, isToday } from '@/lib/format';
import { contractTypeLabel } from '@/lib/domain';
import type { LegalReviewRecord, ReviewRecord } from '@/types/api';

const router = useRouter();
const { role, setRole } = useAppStore();
const { pushToast } = useToast();

const records = ref<LegalReviewRecord[]>([]);
const reviewTraces = ref<Map<string, string>>(new Map());
const loading = ref(true);
const errorMessage = ref('');
const activeTab = ref('pending');
const search = ref('');
const page = ref(1);
const pageSize = 8;

const decisionOpen = ref(false);
const decisionType = ref<'approved' | 'rejected'>('approved');
const activeRecord = ref<LegalReviewRecord | null>(null);
const comment = ref('');
const submitting = ref(false);

async function load() {
  if (role.value !== 'legal') {
    loading.value = false;
    records.value = [];
    return;
  }
  loading.value = true;
  errorMessage.value = '';
  try {
    const [legalRows, reviewRows] = await Promise.all([
      api<LegalReviewRecord[]>('/api/legal-reviews'),
      api<ReviewRecord[]>('/api/reviews'),
    ]);
    records.value = legalRows;
    reviewTraces.value = new Map(reviewRows.map((review) => [review.id, review.trace_id]));
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '复核任务加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(load);

function switchToLegal() {
  setRole('legal');
  pushToast('已切换为法务审核员', { variant: 'success' });
}

const pendingRecords = computed(() => records.value.filter((item) => item.status === 'pending'));
const processedRecords = computed(() => records.value.filter((item) => item.status !== 'pending'));

const todayProcessed = computed(() =>
  processedRecords.value.filter((item) => isToday(item.updated_at || item.created_at)).length,
);

const highRiskPending = computed(() =>
  pendingRecords.value.filter((item) => item.risk_level === 'high' || item.risk_level === 'critical').length,
);

const tabItems = computed(() => [
  { value: 'pending', label: '待处理', count: pendingRecords.value.length },
  { value: 'processed', label: '已处理', count: processedRecords.value.length },
  { value: 'all', label: '全部', count: records.value.length },
]);

const scopedRecords = computed(() => {
  if (activeTab.value === 'pending') return pendingRecords.value;
  if (activeTab.value === 'processed') return processedRecords.value;
  return records.value;
});

const filtered = computed(() => {
  const keyword = search.value.trim().toLowerCase();
  if (!keyword) return scopedRecords.value;
  return scopedRecords.value.filter((item) =>
    [item.title, item.contract_id, item.version, item.comment, item.id]
      .filter(Boolean)
      .some((field) => String(field).toLowerCase().includes(keyword)),
  );
});

const paged = computed(() => filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize));

watch([activeTab, search], () => {
  page.value = 1;
});

watch(filtered, (rows) => {
  const maxPage = Math.max(1, Math.ceil(rows.length / pageSize));
  if (page.value > maxPage) page.value = maxPage;
});

function traceIdFor(record: LegalReviewRecord): string {
  return reviewTraces.value.get(record.review_result_id) || '';
}

function goTrace(record: LegalReviewRecord) {
  const traceId = traceIdFor(record);
  if (!traceId) {
    pushToast('暂未找到对应链路', { description: '审查记录可能已过期或不在最近 100 条范围内。', variant: 'warning' });
    return;
  }
  router.push({ path: '/trace', query: { trace_id: traceId } });
}

function openDecision(record: LegalReviewRecord, decision: 'approved' | 'rejected') {
  activeRecord.value = record;
  decisionType.value = decision;
  comment.value = record.comment || (decision === 'approved' ? '条款风险已确认，同意推进。' : '存在未解决风险，请修改后重新提交。');
  decisionOpen.value = true;
}

async function submitDecision() {
  if (!activeRecord.value) return;
  if (!comment.value.trim()) {
    pushToast('请填写审核意见', { variant: 'warning' });
    return;
  }
  submitting.value = true;
  try {
    await api(`/api/legal-reviews/${activeRecord.value.id}/decision`, {
      method: 'POST',
      body: JSON.stringify({ decision: decisionType.value, comment: comment.value.trim() }),
    });
    pushToast(decisionType.value === 'approved' ? '已通过复核' : '已驳回复核', {
      description: activeRecord.value.title,
      variant: decisionType.value === 'approved' ? 'success' : 'warning',
    });
    decisionOpen.value = false;
    await load();
  } catch (error) {
    pushToast('审核操作失败', {
      description: error instanceof Error ? error.message : '请稍后重试',
      variant: 'error',
    });
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="space-y-4">
    <Card v-if="role !== 'legal'">
      <EmptyState
        title="需要法务权限"
        description="人工复核仅对法务审核员开放。切换身份后可查看待复核队列、审查依据并完成通过或驳回。"
      >
        <template #icon><ShieldAlert class="h-5 w-5" /></template>
        <template #action>
          <Button @click="switchToLegal">
            <ShieldCheck class="h-4 w-4" />
            切换为法务审核员
          </Button>
        </template>
      </EmptyState>
    </Card>

    <template v-else>
      <Alert v-if="errorMessage" variant="destructive" title="复核任务加载失败">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span>{{ errorMessage }}</span>
          <Button size="sm" variant="outline" @click="load">重新加载</Button>
        </div>
      </Alert>

      <div class="grid gap-3 sm:grid-cols-3">
        <StatCard
          title="待处理"
          :value="pendingRecords.length"
          description="需要法务给出结论"
          :icon="ClipboardList"
          tone="amber"
          :loading="loading"
        />
        <StatCard
          title="今日已处理"
          :value="todayProcessed"
          description="今日完成通过或驳回"
          :icon="CalendarCheck2"
          tone="emerald"
          :loading="loading"
        />
        <StatCard
          title="高风险待处理"
          :value="highRiskPending"
          description="高风险与严重风险任务"
          :icon="ShieldAlert"
          tone="red"
          :loading="loading"
        />
      </div>

      <Card>
        <div class="flex flex-col gap-3 border-b border-border p-4 lg:flex-row lg:items-center lg:justify-between">
          <Tabs v-model="activeTab" :items="tabItems" />
          <div class="flex flex-1 items-center gap-2 lg:max-w-md">
            <div class="relative min-w-0 flex-1">
              <Search class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input v-model="search" class="pl-8" placeholder="搜索合同、编号或审核意见" />
            </div>
            <Button variant="outline" size="sm" :disabled="loading" @click="load">
              <RefreshCw :class="['h-4 w-4', loading ? 'animate-spin' : '']" />
              刷新
            </Button>
          </div>
        </div>

        <div v-if="loading" class="space-y-2 p-4">
          <Skeleton v-for="index in 6" :key="index" class="h-12 w-full" />
        </div>

        <EmptyState
          v-else-if="!filtered.length"
          title="暂无复核任务"
          description="当前筛选范围内没有需要处理的法务复核记录。"
        >
          <template #icon><CheckCircle2 class="h-5 w-5" /></template>
        </EmptyState>

        <template v-else>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>合同</TableHead>
                <TableHead class="w-[100px]">风险等级</TableHead>
                <TableHead class="w-[80px]">评分</TableHead>
                <TableHead class="w-[140px]">提交时间</TableHead>
                <TableHead class="w-[100px]">状态</TableHead>
                <TableHead>审核意见</TableHead>
                <TableHead class="w-[190px] text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="record in paged" :key="record.id">
                <TableCell>
                  <div class="min-w-0">
                    <p class="truncate text-[13px] font-medium">{{ record.title }}</p>
                    <p class="mt-0.5 truncate text-[10px] text-muted-foreground">
                      {{ record.contract_id }} · {{ record.version }} · {{ record.id }}
                    </p>
                  </div>
                </TableCell>
                <TableCell><RiskBadge :level="record.risk_level" /></TableCell>
                <TableCell class="text-xs font-medium tabular-nums">{{ record.risk_score }}</TableCell>
                <TableCell class="whitespace-nowrap text-xs text-muted-foreground">
                  {{ formatDateTime(record.status === 'pending' ? record.created_at : record.updated_at || record.created_at) }}
                </TableCell>
                <TableCell><StatusBadge :status="record.status" kind="legal" /></TableCell>
                <TableCell class="max-w-[220px] whitespace-normal text-xs leading-5 text-muted-foreground">
                  {{ record.comment || '—' }}
                </TableCell>
                <TableCell class="text-right">
                  <div class="flex items-center justify-end gap-1">
                    <Button variant="ghost" size="xs" :title="traceIdFor(record) ? '查看审查链路' : '暂无链路记录'" @click="goTrace(record)">
                      <GitBranch class="h-3 w-3" />
                      依据
                    </Button>
                    <template v-if="record.status === 'pending'">
                      <Button variant="outline" size="xs" class="text-red-600 hover:text-red-700" @click="openDecision(record, 'rejected')">
                        <XCircle class="h-3 w-3" />
                        驳回
                      </Button>
                      <Button size="xs" @click="openDecision(record, 'approved')">
                        <CheckCircle2 class="h-3 w-3" />
                        通过
                      </Button>
                    </template>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
          <div class="border-t border-border px-4 py-3">
            <Pagination v-model:page="page" :page-size="pageSize" :total="filtered.length" />
          </div>
        </template>
      </Card>
    </template>

    <Dialog
      v-model:open="decisionOpen"
      :title="decisionType === 'approved' ? '确认通过复核' : '确认驳回复核'"
      :description="activeRecord ? `${activeRecord.title} · ${activeRecord.version}` : ''"
      width="max-w-lg"
      :close-on-overlay="false"
    >
      <div v-if="activeRecord" class="space-y-3">
        <div class="flex flex-wrap items-center gap-2 rounded-lg border border-border bg-muted/30 px-3 py-2.5">
          <RiskBadge :level="activeRecord.risk_level" />
          <span class="text-xs text-muted-foreground">风险评分 {{ activeRecord.risk_score }} 分</span>
          <span class="ml-auto font-mono text-[10px] text-muted-foreground">{{ activeRecord.review_result_id }}</span>
        </div>
        <div
          :class="[
            'rounded-lg border px-3 py-2.5 text-xs leading-5',
            decisionType === 'approved'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300'
              : 'border-red-200 bg-red-50 text-red-800 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300',
          ]"
        >
          {{ decisionType === 'approved' ? '通过后该合同将标记为法务通过，可继续推进签署流程。' : '驳回后需业务调整合同条款，并重新发起审查。' }}
        </div>
        <label class="block space-y-1.5">
          <span class="text-xs font-medium">审核意见</span>
          <Textarea v-model="comment" :rows="4" placeholder="请填写审核依据、风险处置意见或修改要求" />
        </label>
      </div>

      <template #footer>
        <Button variant="outline" :disabled="submitting" @click="decisionOpen = false">取消</Button>
        <Button
          :variant="decisionType === 'approved' ? 'default' : 'destructive'"
          :loading="submitting"
          @click="submitDecision"
        >
          <CheckCircle2 v-if="decisionType === 'approved' && !submitting" class="h-4 w-4" />
          <XCircle v-else-if="!submitting" class="h-4 w-4" />
          {{ decisionType === 'approved' ? '确认通过' : '确认驳回' }}
        </Button>
      </template>
    </Dialog>
  </div>
</template>
