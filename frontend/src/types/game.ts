export enum GameState {
  IDLE = "IDLE",
  QUEUE = "QUEUE",
  MATCH_FOUND = "MATCH_FOUND",
  HERO_SELECT = "HERO_SELECT",
  LOADING = "LOADING",
  IN_GAME = "IN_GAME",
}

export interface DetectionEvidence {
  cropRegions?: { name: string; coords: [number, number, number, number] }[];
  modelUsed?: string;
  escalationUsed?: boolean;
}

export interface Detection {
  state: GameState;
  confidence: number;
  timestamp: string;
  evidence?: DetectionEvidence;
}
