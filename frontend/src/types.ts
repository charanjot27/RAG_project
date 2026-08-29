export type Mode = "local" | "web" | "web_cached";
export type SentenceStatus = "grounded" | "unverified";

export interface Sentence {
  text: string;
  status: SentenceStatus;
  citation: string | null;
  confidence: number;
}

export interface SourceUsed {
  id: string;
  source: string;
  page: number;
  title?: string | null;
}

export interface AskResponse {
  faithfulness_score: number;
  abstained: boolean;
  answer: string;
  grounded_answer: string;
  draft_answer: string;
  mode: Mode;
  timings: Record<string, number>;
  sentences: Sentence[];
  sources_used: SourceUsed[];
}

export interface Health {
  status: string;
  index_ready?: boolean;
  mode?: string;
  chunks?: number | null;
  error?: string;
}
