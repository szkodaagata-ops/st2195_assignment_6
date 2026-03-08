import pandas as pd
import matplotlib.pyplot as plt #for plotting the graph
import re #for splitting the text into words
from collections import Counter #for counting word repetitions

# Load datasets
speeches = pd.read_csv("speeches.csv")
fx = pd.read_csv("fx.csv")

# Keep only columns "date" and "contents" in speeches
speeches = speeches[["date","contents"]]

# Convert date columns to datetime type
speeches["date"] = pd.to_datetime(speeches["date"])
fx["DATE"] = pd.to_datetime(fx["DATE"])


# Merge 2 datasets, keeping all the values from fx as the base
merged_data = fx.merge(speeches, how="left", left_on="DATE", right_on="date")

# Change column name for exchange rate
merged_data = merged_data.rename(
    columns={"US dollar/Euro ECB reference exchange rate (EXR.D.USD.EUR.SP00.A)": "fx"}
)

# Searching for outliers - checking basic statistics
print(merged_data["fx"].describe())

# Checking no value for the day
merged_data["fx"].isna().sum()

# Searching for outliers - checking exchange rate on a plot
merged_data["fx"].plot()
plt.show()

# Update empty records with data from the previous day
clean_data = merged_data.sort_values("DATE").copy()
clean_data["fx"] = clean_data["fx"].ffill()

# Searching for outliers and no value once again
print(clean_data["fx"].describe())
clean_data["fx"].isna().sum()

# Calculating exchange rate return
clean_data = clean_data.sort_values("DATE").copy()
clean_data["return"] = (clean_data["fx"] - clean_data["fx"].shift(1)) / clean_data["fx"].shift(1)

# Extending dataset with 2 new columns concluding good news/bad news on the exchange rate return
clean_data["good_news"] = (clean_data["return"]>0.005).astype(int)
clean_data["bad_news"] = (clean_data["return"]<-0.005).astype(int)

# Remove NA from contents
clean_data = clean_data.dropna()

# Simple stopwords list
stop_words = {
    "the", "and", "of", "to", "in", "a", "for", "is", "on", "that", "by", "with",
    "as", "are", "at", "an", "be", "this", "from", "or", "it", "we", "our", "their",
    "has", "have", "had", "was", "were", "will", "would", "can", "could", "should",
    "may", "might", "not", "but", "than", "which", "who", "whom", "into", "about",
    "also", "these", "those", "its", "they", "them", "he", "she", "his", "her",
    "you", "your", "i", "my", "me", "us"
}

# Function to get 20 top words
def top_words(df, text_col, top_n = 20):
    text = " ".join(df[text_col].astype(str)).lower()
    words = re.findall(r"\b[a-z]+\b", text)
    words = [word for word in words if word not in stop_words]
    word_counts = Counter(words)
    return pd.DataFrame(word_counts.most_common(top_n), columns=["word", "n"])

# Creating good_indicators table with the 20 most common words where good_news = 1
good_indicators = top_words(clean_data[clean_data["good_news"] == 1], "contents", top_n=20)

# Creating bad_indicators table with the 20 most common words where bad_news = 1
bad_indicators = top_words(clean_data[clean_data["bad_news"] == 1], "contents", top_n=20)

# Exporting good_indicators and bad_indicators to CSV
good_indicators.to_csv("good_indicators.csv", index=False)
bad_indicators.to_csv("bad_indicators.csv", index=False)

# Observations: The most common words are very similar for both good and bad news. In both cases the speeches mainly focus on general economic topics such as inflation, policy and growth.