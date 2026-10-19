export interface Contract {
  id: string;
  title: string;
  contract_type: string;
  version: string;
  parent_contract_id?: string | null;
  owner_user_id: string;
  department_id: string;
  status: string;
  amount?: number | null;
  created_at: string;
  content?: string;
}

export interface Clause {
  id: string;
  contract_id: string;
  clause_type: string;
  title: string;
  content: string;
  normalized: Record<string, unknown>;
  sort_order: number;
}

export interface ContractDetail extends Contract {
  clauses: Clause[];
}

export interface ReviewIssue {
  rule_id: string;
  clause_type: string;
  severity: string;
  reason: string;
  suggestion: string;
}

export interface ReviewEvidence {
  id: string;
  title: string;
  version: string;
  clause_type: string;
  content: string;
  rerank_score: number;
}

export interface ReviewSummaryText {
  summary: string;
  business_advice: string;
  disclaimer: string;
}

export interface ClauseDiff {
  clause_type: string;
  title: string;
  actual: Record<string, unknown>;
  standard: Record<string, unknown>;
  changes: string[];
}

export interface ReviewSummary {
  contract_id: string;
  title: string;
  contract_type: string;
  version: string;
  parent_contract_id?: string | null;
  incremental_review: boolean;
  reviewed_clause_types: string[];
  changed_clause_types: string[];
  diffs: ClauseDiff[];
  issues: ReviewIssue[];
  evidence: ReviewEvidence[];
  risk_score: number;
  risk_level: string;
  legal_review_required: boolean;
  summary: ReviewSummaryText;
}

export interface ReviewRunResult extends ReviewSummary {
  review_id: string;
  trace_id: string;
  status: string;
  legal_review_id?: string | null;
}

export interface ReviewRecord {
  id: string;
  contract_id: string;
  trace_id: string;
  risk_score: number;
  risk_level: string;
  legal_review_required: number;
  status: string;
  created_at: string;
  summary: ReviewSummary;
}

export interface LegalReviewRecord {
  id: string;
  review_result_id: string;
  contract_id: string;
  reviewer_role: string;
  status: string;
  comment?: string;
  created_at: string;
  updated_at?: string | null;
  title: string;
  version: string;
  risk_level: string;
  risk_score: number;
}

export interface DashboardData {
  contracts: number;
  reviews: number;
  pending_legal_reviews: number;
  risk_counts: Record<string, number>;
  mock_mode: boolean;
}

export interface TraceEvent {
  id: number;
  trace_id: string;
  node: string;
  detail: Record<string, unknown>;
  latency_ms: number;
  created_at: string;
}

export interface Playbook {
  id: string;
  title: string;
  contract_type: string;
  clause_type: string;
  content: string;
  version: string;
  status: string;
  acl_groups: string;
}

export interface StandardClause {
  id: string;
  contract_type: string;
  clause_type: string;
  standard_text: string;
  version: string;
  status: string;
  required: number;
  severity_if_missing: string;
}

export interface BadCase {
  id: string;
  title: string;
  category: string;
  status: string;
  note: string;
}

export interface EvalCase {
  id: string;
  contract_id: string;
  expected_level: string;
  expected_legal: boolean;
  required_issue: string | null;
  expected_changed_only?: string[];
}

export interface EvalActual {
  risk_level: string;
  legal_review_required: boolean;
  reviewed_clause_types: string[];
  issue_ids: string[];
}

export interface EvalResultRow {
  id: string;
  contract_id: string;
  passed: boolean;
  expected: EvalCase;
  actual: EvalActual;
}

export interface EvalResult {
  passed: number;
  total: number;
  results: EvalResultRow[];
}

export interface RuntimeInfo {
  mock_mode: boolean;
  deepseek_base_url: string;
  deepseek_model: string;
}
