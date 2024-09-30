import pandas as pd
import numpy as np
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_palette("colorblind")
sns.set_style("darkgrid")


# empty values
def empty_val(df: pl.DataFrame) -> pl.DataFrame:
    isna, nunique = [], []
    for col in df.columns:
        isna.append(df[col].is_null().sum() / df.height * 100)
        nunique.append(df[col].cast(pl.Utf8).n_unique())
    return pl.DataFrame({'column': df.columns, 'NaN (%)': isna, 'Nunique': nunique})

# time features
def get_time_features(df: pl.DataFrame, time_col: str):
    df = df.with_columns([
        pl.col(time_col).dt.year().alias('year'),
        pl.col(time_col).dt.month().alias('month'),
        pl.col(time_col).dt.weekday().alias('day of week int'),
        pl.col(time_col).dt.day().alias('day of month'),
        pl.col(time_col).dt.hour().alias('hour')
    ])
    df = df.with_columns([
        pl.when(pl.col('day of week int') > 4)
          .then(pl.lit('weekends'))
          .otherwise(pl.lit('weekdays'))
          .alias('day type')
    ])
    df = df.with_columns([
        pl.when(pl.col('day of week int') == 1).then(pl.lit('Mo'))
        .when(pl.col('day of week int') == 2).then(pl.lit('Tu'))
        .when(pl.col('day of week int') == 3).then(pl.lit('We'))
        .when(pl.col('day of week int') == 4).then(pl.lit('Th'))
        .when(pl.col('day of week int') == 5).then(pl.lit('Fr'))
        .when(pl.col('day of week int') == 6).then(pl.lit('Sa'))
        .otherwise(pl.lit('Su'))
        .alias('day of week')
    ])
    df = df.with_columns([
        pl.when((pl.col('hour') >= 0) & (pl.col('hour') < 3)).then(pl.lit('A (0-3)'))
        .when((pl.col('hour') >= 3) & (pl.col('hour') < 6)).then(pl.lit('B (3-6)'))
        .when((pl.col('hour') >= 6) & (pl.col('hour') < 9)).then(pl.lit('C (6-9)'))
        .when((pl.col('hour') >= 9) & (pl.col('hour') < 12)).then(pl.lit('D (9-12)'))
        .when((pl.col('hour') >= 12) & (pl.col('hour') < 15)).then(pl.lit('E (12-15)'))
        .when((pl.col('hour') >= 15) & (pl.col('hour') < 18)).then(pl.lit('F (15-18)'))
        .when((pl.col('hour') >= 18) & (pl.col('hour') < 21)).then(pl.lit('G (18-21)'))
        .otherwise(pl.lit('H (21-0)')).alias('time window')
    ])
    return df

# get duplicate
def duplicate_col(df: pl.DataFrame, col: str):
    idx_dup = []
    idx_dup_all = []
    percentage = {}
    device_ids = df.select("deviceid").unique().to_series().to_list()
    for id_ in device_ids:
        tmp = df.filter(pl.col('deviceid') == id_)
        grouped = tmp.groupby(col).agg([
            pl.count(col).alias("count")
        ])
        total_dupes = grouped.filter(pl.col("count") > 1).select(pl.col("count").sum()).item()
        possible_dupes = total_dupes - grouped.filter(pl.col("count") > 1).height
        percent_dup = possible_dupes / tmp.height * 100 if tmp.height > 0 else 0
        percentage[id_] = percent_dup
        tmp = tmp.with_columns([
            pl.col(col).is_duplicated().over(col).alias('is_duplicated'),
            pl.col(col).is_first().over(col).alias('is_first')
        ])

        dup_indices = tmp.filter(
            pl.col('is_duplicated') & ~pl.col('is_first')
        ).select(pl.col("row_nr")).to_series().to_list()
        idx_dup += dup_indices
        dup_all_indices = tmp.filter(
            pl.col('is_duplicated')
        ).select(pl.col("row_nr")).to_series().unique().to_list()
        idx_dup_all += dup_all_indices
        
    ids = list(percentage.keys())
    vals = [percentage[i] for i in ids]
    
    tmp_df = pl.DataFrame({'deviceid': ids, 'percentage': vals}).to_pandas()
    tmp_df = tmp_df.sort_values(by='percentage', ascending=False)
    tmp_df['deviceid'] = tmp_df['deviceid'].astype('category')
    tmp_df['deviceid'].cat.reorder_categories(tmp_df['deviceid'], ordered=True, inplace=True)
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.barplot(x='deviceid', y='percentage', data=tmp_df, ax=ax, order=tmp_df['deviceid'])
    ax.set_title('Duplicated Timestamps')
    plt.show()

    return idx_dup, idx_dup_all

# round to nearest half
def round_to_nearest_half(data):
    return (data * 2).round() / 2

# get rounded coordinates
def round_to_nearest_half_int_coord(df):
    df = df.with_columns([
        # Simpan latitude dan longitude asli
        pl.col("latitude").alias("Lat6"),
        pl.col("longitude").alias("Long6"),

        # Membulatkan latitude dan longitude ke angka setengah terdekat (3 digit)
        (round_to_nearest_half(pl.col("latitude") * 1e3) / 1e3).alias("Lat3"),
        (round_to_nearest_half(pl.col("longitude") * 1e3) / 1e3).alias("Long3"),

        # Membulatkan latitude dan longitude ke 4 digit
        ((pl.col("latitude") * 1e4).round() / 1e4).alias("Lat4"),
        ((pl.col("longitude") * 1e4).round() / 1e4).alias("Long4")
    ])

    return df.drop(["latitude", "longitude"])

# # get rounded coordinates
# def ceil_coord(df):
#     df['Lat6'] = df['latitude']
#     df['Long6'] = df['longitude']
#     df['Lat2'] = np.ceil(df['Lat6']*1e2) / 1e2
#     df['Long2'] = np.ceil(df['Long6']*1e2) / 1e2
#     df['Lat3'] = np.ceil(df['Lat6']*1e3) / 1e3
#     df['Long3'] = np.ceil(df['Long6']*1e3) / 1e3
#     df['Lat4'] = np.ceil(df['Lat6']*1e4) / 1e4
#     df['Long4'] = np.ceil(df['Long6']*1e4) / 1e4
#     df['Lat5'] = np.ceil(df['Lat6']*1e5) / 1e5
#     df['Long5'] = np.ceil(df['Long6']*1e5) / 1e5
#     return df.drop(['latitude', 'longitude'], axis=1)

        
# get aggregation of speed and acceleration
def agg_speed_accel(df):
    agg_speed, agg_accel = {}, {}
    for id_ in df['deviceid'].unique():
        data = df[df['deviceid']==id_]
        # only take into account when vehicles move
        data = data[data['speed']!=0]  
        # aggregation of speed & acceleration
        speed, accel = {}, {}
        for dec in [2, 3, 4, 5]:
            tmp = data.groupby([f'Lat{dec}', f'Long{dec}'])['speed'].agg(['count', 'mean']).reset_index()
            speed.update({dec: tmp})
            tmp = data.groupby([f'Lat{dec}', f'Long{dec}'])['accel'].mean().reset_index()
            accel.update({dec: tmp})
        agg_speed.update({id_: speed})    
        agg_accel.update({id_: accel})
    return agg_speed, agg_accel
