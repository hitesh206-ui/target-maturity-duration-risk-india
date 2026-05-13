# Raw G-Sec Yield CSV Upload Folder

Use this folder when automated daily yield download is unavailable.

## Required Files

Upload CSV files using this exact naming convention:

```text
india_1y_yield.csv
india_2y_yield.csv
india_3y_yield.csv
india_5y_yield.csv
```

Optional:

```text
india_3m_yield.csv
```

## Expected Columns

The import script accepts common formats from public financial portals such as Investing.com:

```text
Date,Price,Open,High,Low,Change %
```

or a simplified format:

```text
date,yield_percent
```

For Investing.com-style files, the `Price` column is treated as the closing yield in percent.

## Date Range

Target range:

```text
2024-01-01 to 2026-05-13
```

## Source Logging

After uploading files, update:

```text
data/documentation/source_log.csv
```

with the source URL, access date, and notes.
