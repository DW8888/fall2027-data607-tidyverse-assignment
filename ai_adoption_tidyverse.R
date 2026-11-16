# ==========================================
# Project: AI Adoption and Developer Attitudes
# Dataset: 2025 Stack Overflow Developer Survey
# Course: DATA 607
# ==========================================

# 1. Load Tidyverse

library(tidyverse)

# 2. Import the dataset

ai_data <- read_csv("results.CSV")

# 3. Select AI-related variables

ai_focus <- ai_data %>%
  select(AISelect, AISent, AIAcc, AIThreat)

# 4. Explore the selected variables
glimpse(ai_focus)

# 5. Examine the first six observations
head(ai_focus)

# 6. Count AI adoption responses
ai_adoption <- ai_focus %>%
  count(AISelect, sort = TRUE)

print(ai_adoption)

# 7. Calculate AI adoption percentages

ai_adoption <- ai_focus %>%
  count(AISelect) %>%
  mutate(
    percentage = round(n / sum(n) * 100, 2)
  )

print(ai_adoption)

# 8. Visualize AI adoption

ggplot(ai_adoption, aes(x = AISelect, y = percentage)) +
  geom_col(fill = "steelblue") +
  labs(
    title = "AI Adoption Among Developers",
    x = "AI Adoption Frequency",
    y = "Percentage (%)"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# 9. Calculate AI adoption percentages without missing responses

ai_adoption_clean <- ai_focus %>%
  filter(!is.na(AISelect)) %>%
  count(AISelect, sort = TRUE) %>%
  mutate(
    percentage = round(n / sum(n) * 100, 2)
  )

print(ai_adoption_clean)
