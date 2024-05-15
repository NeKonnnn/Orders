from pathlib import Path
from typing import Mapping, Optional, Sequence, Dict

import numpy as np
import polars as pl

metric_k = 10
ndcg_weights = 1.0 / np.log2(np.arange(0, metric_k) + 2)
ndcg_idcg = ndcg_weights.cumsum()


def hits_per_user(pl_struct: Mapping[str, Sequence[int]]) -> Optional[np.ndarray]:
    predicted = pl_struct["predicted"]
    ground_truth = pl_struct["ground_truth"]

    if predicted is None:
        return None

    assert ground_truth is not None
    assert len(ground_truth) > 0

    predicted_np = np.array(predicted[:metric_k])
    ground_truth_np = np.array(ground_truth)

    hits = (predicted_np.reshape(-1, 1) == ground_truth_np.reshape(1, -1)).sum(axis=1)
    return hits


def recall_per_user(pl_struct: Mapping[str, Sequence[int]]) -> float:
    hits = hits_per_user(pl_struct)

    if hits is None:
        return 0.0

    gt_count = min(len(pl_struct["ground_truth"]), metric_k)
    return hits.sum() / gt_count


def ndcg_per_user(pl_struct: Mapping[str, Sequence[int]]) -> float:
    hits = hits_per_user(pl_struct)

    if hits is None:
        return 0.0

    predicted_count = min(len(pl_struct["predicted"]), metric_k)
    gt_count = min(len(pl_struct["ground_truth"]), metric_k)

    dcg = (hits * ndcg_weights[:predicted_count]).sum()
    idcg = ndcg_idcg[gt_count - 1]
    ndcg = dcg / idcg

    return ndcg


def compute_metrics(submission: pl.DataFrame, gt: pl.DataFrame) -> Dict[str, float]:
    submission_postprocessed = (
        submission
        .select(
            pl.col("user_id").cast(pl.Int32),
            pl.col("track_id").str.split(" ").cast(pl.List(pl.Int32)).alias("predicted"),
        )
        .unique(subset="user_id")

        # Remove duplicated items
        # IMPORTANT: We keep original order of items, because it affects metric value
        .with_columns(
            pl.col("predicted").list.unique(maintain_order=True)
        )
    )

    ground_truth = gt.groupby("user_id").agg(pl.col("track_id").alias("ground_truth"))
    submission_with_gt = ground_truth.join(submission_postprocessed, on="user_id", how="left")

    metrics_per_user = submission_with_gt.select(
        pl.col("user_id"),
        pl.struct("predicted", "ground_truth").apply(ndcg_per_user).alias("ndcg"),
        pl.struct("predicted", "ground_truth").apply(recall_per_user).alias("recall"),
    )

    mean_ndcg = metrics_per_user.select(pl.col("ndcg").mean())["ndcg"][0]
    mean_recall = metrics_per_user.select(pl.col("recall").mean())["recall"][0]

    return {
        f"ndcg@{metric_k}": mean_ndcg,
        f"recall@{metric_k}": mean_recall,
    }