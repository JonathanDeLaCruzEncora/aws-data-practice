import pandas as pd
import numpy as np

#data gathered from Kaggle: https://www.kaggle.com/datasets/aliredaelblgihy/social-media-engagement-report
df  = pd.read_excel("/content/social_media_engagement_data.xlsx")

df_sample = df.iloc[:int(len(df) * 0.001)]
df_parts = np.array_split(df_sample, 4)

for i, part in enumerate(df_parts):
    part.to_csv(f'batch_data_sample{i+1}.csv', index=False)