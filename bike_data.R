# Load required packages
library(osmdata)
library(sf)
library(dplyr)
library(ggplot2)
library(leaflet)

# Define the bounding box for Montreal
montreal_bbox <- c(-73.9860, 45.4121, -73.4730, 45.7006)

# Download bike-sharing stations and cycling infrastructure data for Montreal
bike_sharing_query <- opq(bbox = montreal_bbox) %>%
  add_osm_feature(key = "amenity", value = "bicycle_rental") %>%
  osmdata_sf()

cycling_infra_query <- opq(bbox = montreal_bbox) %>%
  add_osm_feature(key = "highway", value = "cycleway") %>%
  osmdata_sf()

# Count the total number of bike-sharing stations
total_stations <- nrow(bike_sharing_query$osm_points)

# Calculate the total length of cycling infrastructure
total_infra_length <- sum(st_length(cycling_infra_query$osm_lines), na.rm = TRUE)

# Create a data frame with the calculated values
montreal_data <- data.frame(
  category = c("Bike-Sharing Stations", "Cycling Infrastructure Length (km)"),
  value = c(total_stations, total_infra_length / 1000)
)

# Visualize the data using a bar chart
bar_plot <- ggplot(montreal_data, aes(x = category, y = value)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  theme_minimal() +
  labs(title = "Montreal Bike-Sharing Stations and Cycling Infrastructure",
       x = "Category",
       y = "Value")

# Print the total number of bike-sharing stations and the total length of cycling infrastructure
cat(paste0("Total bike-sharing stations: ", total_stations, "\n"))
cat(paste0("Total cycling infrastructure length: ", total_infra_length, " km\n"))

# Calculate the ratio of bike-sharing stations per 0.5 km of cycling infrastructure
stations_per_half_km <- total_stations / (total_infra_length / 2)

# Print the ratio
cat(paste0("There are ", round(stations_per_half_km, 2), " bike-sharing stations per 0.5 km of cycling infrastructure in Montreal.\n"))

# Calculate the ratio of bike-sharing stations per linear km of cycling infrastructure
stations_per_km <- total_stations / (total_infra_length / 1000)

# Print the ratio
cat(paste0("There are ", round(stations_per_km, 2), " bike-sharing stations per linear km of cycling infrastructure in Montreal.\n"))

# Create a leaflet map showing the bike-sharing stations
bike_sharing_map <- leaflet(bike_sharing_query$osm_points) %>%
  addTiles() %>%
  addMarkers(clusterOptions = markerClusterOptions())

# Display the bar chart and the leaflet map
print(bar_plot)
print(bike_sharing_map)
