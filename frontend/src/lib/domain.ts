export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type StatusKind = 'review' | 'legal' | 'contract' | 'badcase';

export const RISK_ORDER: RiskLevel[] = ['low', 'medium', 'high', 'critical'];

export const RISK_LABELS: Record<string, string> = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '严重风险',
};

export const RISK_CHART_COLORS: Record<string, string> = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#f97316',
  critical: '#ef4444',
};

export const RISK_BADGE_CLASSES: Record<string, string> = {
  low: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300',
  medium: 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300',
  high: 'border-orange-200 bg-orange-50 text-orange-700 dark:border-orange-500/30 dark:bg-orange-500/10 dark:text-orange-300',
  critical: 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300',
};

export const RISK_BAR_CLASSES: Record<string, string> = {
  low: 'bg-emerald-500',
  medium: 'bg-amber-500',
  high: 'bg-orange-500',
  critical: 'bg-red-500',
};

export const CONTRACT_TYPES = [
  { value: 'saas', label: 'SaaS 服务' },
  { value: 'sales', label: '销售合同' },
  { value: 'purchase', label: '采购合同' },
  { value: 'nda', label: '保密协议' },
  { value: 'channel', label: '渠道合作' },
  { value: 'dpa', label: '数据处理' },
];

const CONTRACT_TYPE_MAP = Object.fromEntries(CONTRACT_TYPES.map((item) => [item.value, item.label]));

export const CLAUSE_TYPES = {
  payment: '付款条款',
  liability: '责任限制',
  ip: '知识产权',
  renewal: '续约条款',
  termination: '合同终止',
  jurisdiction: '争议管辖',
};

export const TRACE_NODE_ORDER = ['incremental_diff', 'clause_diff', 'rule_check', 'legal_rag', 'recommendation'];

export const TRACE_NODE_LABELS: Record<string, string> = {
  incremental_diff: '增量差异识别',
  clause_diff: '条款差异比对',
  rule_check: '红线规则校验',
  legal_rag: 'Playbook 检索',
  recommendation: 'AI 建议生成',
};

export const REVIEW_STATUS_LABELS: Record<string, string> = {
  waiting_legal_review: '待法务复核',
  precheck_passed: '初审通过',
  legal_approved: '法务通过',
  legal_rejected: '法务驳回',
  pending: '待审核',
  approved: '已通过',
  rejected: '已驳回',
};

export const CONTRACT_STATUS_LABELS: Record<string, string> = {
  active: '生效中',
  draft: '草稿',
  archived: '已归档',
  terminated: '已终止',
};

export const BAD_CASE_STATUS_LABELS: Record<string, string> = {
  open: '待处理',
  fixed: '已修复',
  pending: '待处理',
};

export const BAD_CASE_CATEGORY_LABELS: Record<string, string> = {
  retrieval: '检索召回',
  clause_extraction: '条款抽取',
  cost: '成本效率',
  reasoning: '推理判断',
  other: '其他',
};

export const BAD_CASE_CATEGORIES = [
  { value: 'retrieval', label: '检索召回' },
  { value: 'clause_extraction', label: '条款抽取' },
  { value: 'cost', label: '成本效率' },
  { value: 'reasoning', label: '推理判断' },
  { value: 'other', label: '其他' },
];

const STATUS_CLASSES: Record<string, Record<string, string>> = {
  review: {
    waiting_legal_review: 'border-sky-200 bg-sky-50 text-sky-700 dark:border-sky-500/30 dark:bg-sky-500/10 dark:text-sky-300',
    precheck_passed: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300',
    legal_approved: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300',
    legal_rejected: 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300',
  },
  legal: {
    pending: 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300',
    approved: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300',
    rejected: 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300',
  },
  contract: {
    active: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300',
    draft: 'border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-500/30 dark:bg-slate-500/10 dark:text-slate-300',
    archived: 'border-slate-200 bg-slate-50 text-slate-500 dark:border-slate-500/30 dark:bg-slate-500/10 dark:text-slate-400',
    terminated: 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300',
  },
  badcase: {
    open: 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300',
    pending: 'border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300',
    fixed: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300',
  },
};

const DEFAULT_STATUS_CLASS = 'border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-500/30 dark:bg-slate-500/10 dark:text-slate-300';

export function riskLabel(level?: string | null): string {
  if (!level) return '未评估';
  return RISK_LABELS[level] || level;
}

export function riskBadgeClass(level?: string | null): string {
  return (level && RISK_BADGE_CLASSES[level]) || DEFAULT_STATUS_CLASS;
}

export function statusLabel(status?: string | null, kind: StatusKind = 'review'): string {
  if (!status) return '未知';
  const labels = kind === 'contract' ? CONTRACT_STATUS_LABELS : kind === 'badcase' ? BAD_CASE_STATUS_LABELS : REVIEW_STATUS_LABELS;
  return labels[status] || status;
}

export function statusBadgeClass(status?: string | null, kind: StatusKind = 'review'): string {
  if (!status) return DEFAULT_STATUS_CLASS;
  return STATUS_CLASSES[kind]?.[status] || DEFAULT_STATUS_CLASS;
}

export function contractTypeLabel(value?: string | null): string {
  if (!value) return '未分类';
  return CONTRACT_TYPE_MAP[value] || value;
}

export function clauseTypeLabel(value?: string | null): string {
  if (!value) return '未分类';
  return CLAUSE_TYPES[value as keyof typeof CLAUSE_TYPES] || value;
}

export function traceNodeLabel(node?: string | null): string {
  if (!node) return '未知节点';
  return TRACE_NODE_LABELS[node] || node;
}

export function badCaseCategoryLabel(value?: string | null): string {
  if (!value) return '未分类';
  return BAD_CASE_CATEGORY_LABELS[value] || value;
}

export function isRiskLevel(value: string): value is RiskLevel {
  return RISK_ORDER.includes(value as RiskLevel);
}

const FIELD_LABELS: Record<string, string> = {
  payment_days: '付款周期（天）',
  payment_trigger: '付款触发条件',
  liability_cap: '责任上限',
  background_ip_owner: '背景知识产权归属',
  source_code_delivery: '是否交付源代码',
  auto_renewal: '是否自动续约',
  renewal_months: '续约周期（月）',
  unilateral_termination_customer_only: '仅客户可单方终止',
  jurisdiction: '争议管辖地',
};

const VALUE_LABELS: Record<string, string> = {
  invoice_received: '收到发票后',
  contract_amount: '合同总金额',
  original_owner: '原始权利人',
  provider_location: '服务提供方所在地',
  customer_location: '客户所在地',
  mutual: '双方协商确定',
  true: '是',
  false: '否',
};

export function fieldLabel(key: string): string {
  return FIELD_LABELS[key] || key;
}

export function formatFieldValue(_key: string, value: unknown): string {
  if (value === null || value === undefined || value === '') return '未约定';
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (typeof value === 'number') return String(value);
  const text = String(value);
  return VALUE_LABELS[text] || text;
}

export function formatDiffValue(value: string): string {
  const trimmed = value.trim();
  if (trimmed === 'None') return '未约定';
  if (trimmed === 'True') return '是';
  if (trimmed === 'False') return '否';
  const unquoted = trimmed.replace(/^['"]|['"]$/g, '');
  return VALUE_LABELS[unquoted] || unquoted;
}

export function parseDiffChange(change: string): { key: string; from: string; to: string } {
  const colonIndex = change.indexOf(':');
  const key = colonIndex > -1 ? change.slice(0, colonIndex) : change;
  const rest = colonIndex > -1 ? change.slice(colonIndex + 1) : '';
  const arrowIndex = rest.indexOf('->');
  if (arrowIndex === -1) return { key: fieldLabel(key), from: '', to: rest.trim() };
  return {
    key: fieldLabel(key.trim()),
    from: formatDiffValue(rest.slice(0, arrowIndex)),
    to: formatDiffValue(rest.slice(arrowIndex + 2)),
  };
}
