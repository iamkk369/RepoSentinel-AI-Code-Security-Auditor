export interface Repository {
  id: number
  full_name: string
  html_url: string
  description: string | null
  language: string | null
  visibility: string
  default_branch: string
}

export interface Scan {
  id: number
  repository_id: number
  status: string
  branch: string
  total_findings: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  info_count: number
  created_at: string
}

export interface Finding {
  id: number
  finding_id: string
  scanner: string
  category: string
  title: string
  description: string
  severity: string
  affected_file: string | null
  line_number: number | null
  vulnerability_id: string | null
  evidence: string | null
  remediation: string | null
  created_at: string
}
