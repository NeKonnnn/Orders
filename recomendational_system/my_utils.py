import polars as pl

def make_submission(recommendations: pl.DataFrame) -> pl.DataFrame:
    submission = (
        recommendations
        .with_columns(pl.col("track_id").cast(pl.Utf8))
        .group_by("user_id")
        .agg(
            pl.col("track_id")
            .sort_by("score", descending=True)
        )
        .with_columns(
            pl.col("track_id").list.join(" ")
        )
    )
    return submission