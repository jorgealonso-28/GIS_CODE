library(readxl)
library(ggplot2)
library(extrafont)
library(showtext)
library(systemfonts)
setwd("G:/Shared drives/LLC   Technology/3.Resilience team/Biodiversity Product Project/3. Scientific and Resilience readiness/Pilot projects 2024-2025/Pino 24-25 pilot/maps and shapefiles/GEE")

# Data Import
NDVI_reference <- read_excel("Reference_site/Data/Reference_NDVI.xlsx", range = "I1:K31")
NDMI_reference <- read_excel("Reference_site/Data/Reference_NDMI.xlsx", range = "I1:K31")
NDVI_NEnergy <- read_excel("Pino_24_25/Data/PinoNE_NDVI.xlsx", range = "I1:K31")
NDMI_NEnergy <- read_excel("Pino_24_25/Data/PinoNE_NDMI.xlsx", range = "I1:K31")

# Ensure 'Season - Year' retains its original order by converting it to a factor
NDVI_reference$Year <- sub(".*(\\d{4})$", "\\1", NDVI_reference$`Season summary`)
NDVI_reference$Season <- sub(" .*", "", NDVI_reference$`Season summary`)

NDMI_reference$Year <- sub(".*(\\d{4})$", "\\1", NDMI_reference$`Season summary`)
NDMI_reference$Season <- sub(" .*", "", NDMI_reference$`Season summary`)

NDVI_NEnergy$Year <- sub(".*(\\d{4})$", "\\1", NDVI_NEnergy$`Season summary`)
NDVI_NEnergy$Season <- sub(" .*", "", NDVI_NEnergy$`Season summary`)

NDMI_NEnergy$Year <- sub(".*(\\d{4})$", "\\1", NDMI_NEnergy$`Season summary`)
NDMI_NEnergy$Season <- sub(" .*", "", NDMI_NEnergy$`Season summary`)

#Years fractions
NDVI_reference$YearJittered <- as.numeric(NDVI_reference$Year) +
  ifelse(NDVI_reference$Season == "Winter", 0.1,
         ifelse(NDVI_reference$Season == "Spring", 0.3,
                ifelse(NDVI_reference$Season == "Summer", 0.5, 0.7)))
NDMI_reference$YearJittered <- as.numeric(NDMI_reference$Year) +
  ifelse(NDMI_reference$Season == "Winter", 0.1,
         ifelse(NDMI_reference$Season == "Spring", 0.3,
                ifelse(NDMI_reference$Season == "Summer", 0.5, 0.7)))
NDVI_NEnergy$YearJittered <- as.numeric(NDVI_NEnergy$Year) +
  ifelse(NDVI_NEnergy$Season == "Winter", 0.1,
         ifelse(NDVI_NEnergy$Season == "Spring", 0.3,
                ifelse(NDVI_NEnergy$Season == "Summer", 0.5, 0.7)))
NDMI_NEnergy$YearJittered <- as.numeric(NDMI_NEnergy$Year) +
  ifelse(NDMI_NEnergy$Season == "Winter", 0.1,
         ifelse(NDMI_NEnergy$Season == "Spring", 0.3,
                ifelse(NDMI_NEnergy$Season == "Summer", 0.5, 0.7)))

# Define existing color palette
custom_colors <- c(
  "Summer" = "#FFD700",  # Bright Gold/Yellow for Summer Sun
  "Autumn" = "#D2691E",  # Chocolate Brown for Autumn Leaves
  "Winter" = "#4682B4",  # Steel Blue for Winter Chill
  "Spring" = "#32CD32"   # Lime Green for Fresh Spring Growth
)


# Create the plots
# NDVI for the reference site
NDVI_ref_plot <- ggplot(NDVI_reference, aes(x = YearJittered, y = Average, color = `Season type`)) +
  geom_point(size = 4) +  # Add points, colored by 'Season - Type'
  geom_line(aes(group = 1), color = "gray", linetype = "dashed") +  # Connect points with a line
  scale_x_continuous(breaks = unique(as.numeric(NDVI_NEnergy$Year)), labels = unique(NDVI_NEnergy$Year)) +
  theme_minimal() +  # Minimal theme for a clean look
  scale_color_manual(values = custom_colors) +  # Map colors to Season - Type
  labs(
    title = "Average NDVI by Season and Year - Reference site",
    x = "Year",
    y = "Average NDVI (-1, 1)",
    color = "Season"  # Legend title
  ) +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate X-axis labels
    text = element_text(family = "Avenir LT Pro 45 Book", face = "plain")
  )
# NDMI for the reference site
NDMI_ref_plot <- ggplot(NDMI_reference, aes(x = YearJittered, y = Average, color = `Season type`)) +
  geom_point(size = 4) +  # Add points, colored by 'Season - Type'
  geom_line(aes(group = 1), color = "gray", linetype = "dashed") +  # Connect points with a line
  scale_x_continuous(breaks = unique(as.numeric(NDVI_NEnergy$Year)), labels = unique(NDVI_NEnergy$Year)) +
  theme_minimal() +  # Minimal theme for a clean look
  scale_color_manual(values = custom_colors) +  # Map colors to Season - Type
  labs(
    title = "Average NDMI by Season and Year - Reference site",
    x = "Year",
    y = "Average NDMI (-1, 1)",
    color = "Season"  # Legend title
  ) +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate X-axis labels
    text = element_text(family = "Avenir LT Pro 45 Book", face = "plain")
  )

# NDVI for the NEnergy site
NDVI_NE_plot <- ggplot(NDVI_NEnergy, aes(x = YearJittered, y = Average, color = `Season type`)) +
  geom_point(size = 4) +  # Add points, colored by 'Season - Type'
  geom_line(aes(group = 1), color = "gray", linetype = "dashed") +  # Connect points with a line
  scale_x_continuous(breaks = unique(as.numeric(NDVI_NEnergy$Year)), labels = unique(NDVI_NEnergy$Year)) +
  theme_minimal() +  # Minimal theme for a clean look
  scale_color_manual(values = custom_colors) +  # Map colors to Season - Type
  labs(
    title = "Average NDVI by Season and Year - Baseline - Pinofranqueado",
    x = "Year",
    y = "Average NDVI (-1, 1)",
    color = "Season"  # Legend title
  ) +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate X-axis labels
    text = element_text(family = "Avenir LT Pro 45 Book", face = "plain")
  )

# NDMI for the NEnergy site
NDMI_NE_plot <- ggplot(NDMI_NEnergy, aes(x = YearJittered, y = Average, color = `Season type`)) +
  geom_point(size = 4) +  # Add points, colored by 'Season - Type'
  geom_line(aes(group = 1), color = "gray", linetype = "dashed") +  # Connect points with a line
  scale_x_continuous(breaks = unique(as.numeric(NDVI_NEnergy$Year)), labels = unique(NDVI_NEnergy$Year)) +
  theme_minimal() +  # Minimal theme for a clean look
  scale_color_manual(values = custom_colors) +  # Map colors to Season - Type
  labs(
    title = "Average NDMI by Season and Year - Baseline - Pinofranqueado",
    x = "Year",
    y = "Average NDMI (-1, 1)",
    color = "Season"  # Legend title
  ) +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate X-axis labels
    text = element_text(family = "Avenir LT Pro 45 Book", face = "plain")
  )

# Display the plots
print(NDVI_ref_plot)
print(NDMI_ref_plot)
print(NDVI_NE_plot)
print(NDMI_NE_plot)

ggsave(filename = "NDMI_NE_plot.svg",  # Specify the file name
  plot = NDMI_NE_plot,           # The plot object to save
  device = "svg",             # Set the device to SVG
  width = 10,                 # Width of the plot
  height = 7,                 # Height of the plot
  units = "in",               # Specify units (inches)
  dpi = 300                   # Set the resolution (though not critical for SVG)
)

