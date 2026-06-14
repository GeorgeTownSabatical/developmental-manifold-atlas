export type AccessTier = "synthetic" | "public" | "aggregate" | "restricted" | "metadata-only";

export interface DatasetRecord {
  dataset_id: string;
  title: string;
  species: string[];
  access_tier: AccessTier;
}

