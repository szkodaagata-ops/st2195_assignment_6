library(readr)
library(dplyr)
library(tidyr)
library(tidytext)

# Load datasets
speeches <- read_csv("speeches.csv")
fx <- read_csv("fx.csv")

# Keep only columns "date" and "contents" in speeches
speeches <- speeches %>%
  select(date, contents)

# Merge 2 datasets, keeping all the values from fx as the base
merged_data <- left_join(fx, speeches, by = c("DATE" = "date"))

# Searching for outliers - checking basic statistics
summary(merged_data)

# Searching for outliers - checking exchange rate on the boxplot
plot(merged_data$`US dollar/Euro ECB reference exchange rate (EXR.D.USD.EUR.SP00.A)`)

# Update empty records with data from the previous day
clean_data <- merged_data %>%
  arrange(DATE) %>%
  fill(`US dollar/Euro ECB reference exchange rate (EXR.D.USD.EUR.SP00.A)`,
       .direction = "down")

# Checking statistics, including empty cells once again
summary(clean_data)

# Change column name for exchange rate
clean_data <- clean_data %>%
  rename(fx = `US dollar/Euro ECB reference exchange rate (EXR.D.USD.EUR.SP00.A)`)

# Calculating exchange rate return
clean_data <- clean_data %>%
  arrange(DATE) %>%
  mutate(return = (fx - lag(fx)) / lag(fx))

# Extending datasent with 2 new columns concluding good news/bad news on the exchange rate return
clean_data <- clean_data %>%
  mutate(
    good_news = case_when(
      return > 0.005 ~ 1,
      TRUE ~ 0
    ),
    bad_news = case_when(
      return < -0.005 ~ 1,
      TRUE ~ 0
    )
  )

# Remove NA from "contents"
clean_data <- clean_data %>%
  na.omit()

# Creating good_indicators table with the 20 most common words where good_news = 1
good_indicators <- clean_data %>%
  filter(good_news == 1) %>%  #filter on good_news = 1
  unnest_tokens(word, contents) %>% #split text into words
  anti_join(stop_words) %>% #remove stop words
  count(word, sort = TRUE) %>%  #count word repetition
  slice_head(n=20) #select 20 the most occurring words

# Creating bad_indicators table with the 20 most common words where bad_news = 1
bad_indicators <- clean_data %>%
  filter(bad_news == 1) %>% #filter on bad_news = 1
  unnest_tokens(word, contents) %>% #split text into words
  anti_join(stop_words) %>% #remove stop words
  count(word, sort = TRUE) %>% #count word repetition
  slice_head(n=20) #select 20 the most occuring words

# Exporting good_indicators and bad_indicators to CSV
write_csv(good_indicators, "good_indicators.csv")
write_csv(bad_indicators, "bad_indicators.csv")

# Observations: The most common words are very similar for both good and bad news. In both cases the speeches mainly focus on general economic topics such as inflation, policy and growth.
  