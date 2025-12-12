#!/bin/bash
# ==============================================================================
# AUTOMATED STATE MAP FIX SCRIPT
# ==============================================================================
# This script automatically updates server_overview.R to fix the state map
# ==============================================================================

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🗺️  AUTOMATED STATE MAP FIX"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Navigate to project directory
cd ~/Library/CloudStorage/OneDrive-american.edu/Personal/portfolio_projects/gp-food-basket

# Check if server_overview.R exists
if [ ! -f "R/server_overview.R" ]; then
    echo "❌ Error: R/server_overview.R not found!"
    exit 1
fi

echo "📋 Step 1: Backing up server_overview.R..."
cp R/server_overview.R R/server_overview_backup_$(date +%Y%m%d_%H%M%S).R
echo "✅ Backup created"
echo ""

echo "🔧 Step 2: Creating fixed version..."

# Create the fixed server file with R
R --vanilla --silent << 'EOF'

# Read the current server file
server_code <- readLines("R/server_overview.R")

# Find where to insert the state lookup (before output$state_map)
state_map_line <- grep("output\\$state_map.*<-.*renderPlot", server_code)[1]

if (is.na(state_map_line)) {
  cat("❌ Could not find output$state_map section!\n")
  quit(status = 1)
}

# State lookup table code to insert
lookup_code <- c(
  "  # ==========================================================================",
  "  # STATE NAME LOOKUP (for map conversion)",
  "  # ==========================================================================",
  "  ",
  "  state_name_lookup <- tibble(",
  "    state = c(",
  '      "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",',
  '      "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",',
  '      "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",',
  '      "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",',
  '      "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"',
  "    ),",
  "    state_name = c(",
  '      "alabama", "alaska", "arizona", "arkansas", "california", "colorado",',
  '      "connecticut", "delaware", "district of columbia", "florida",',
  '      "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas",',
  '      "kentucky", "louisiana", "maine",',
  '      "maryland", "massachusetts", "michigan", "minnesota", "mississippi",',
  '      "missouri", "montana", "nebraska", "nevada", "new hampshire",',
  '      "new jersey", "new mexico", "new york", "north carolina", "north dakota",',
  '      "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island",',
  '      "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont",',
  '      "virginia", "washington", "west virginia", "wisconsin", "wyoming"',
  "    )",
  "  )",
  "  "
)

# Find the end of the state_map renderPlot block
brace_count <- 0
in_block <- FALSE
end_line <- state_map_line

for (i in state_map_line:length(server_code)) {
  line <- server_code[i]
  
  if (grepl("renderPlot\\(\\{", line)) {
    in_block <- TRUE
    brace_count <- brace_count + 1
  }
  
  if (in_block) {
    brace_count <- brace_count + stringr::str_count(line, "\\{")
    brace_count <- brace_count - stringr::str_count(line, "\\}")
    
    if (brace_count == 0) {
      end_line <- i
      break
    }
  }
}

# New state_map code
new_map_code <- c(
  "  output$state_map <- renderPlot({",
  "    state_data <- year_data() %>%",
  "      group_by(state) %>%",
  "      summarise(",
  "        avg_fi = mean(overall_food_insecurity_rate, na.rm = TRUE),",
  "        .groups = \"drop\"",
  "      ) %>%",
  "      # Convert state abbreviations to full lowercase names",
  "      left_join(state_name_lookup, by = \"state\")",
  "    ",
  "    # Get US map data",
  "    us_map <- map_data(\"state\")",
  "    ",
  "    # Join with our data using full state names",
  "    map_data_merged <- us_map %>%",
  "      left_join(state_data, by = c(\"region\" = \"state_name\"))",
  "    ",
  "    ggplot(map_data_merged, aes(x = long, y = lat, group = group, fill = avg_fi * 100)) +",
  "      geom_polygon(color = \"white\", size = 0.5) +",
  "      scale_fill_gradient2(",
  "        low = \"#06D6A0\",",
  "        mid = \"#F4A261\",",
  "        high = \"#E63946\",",
  "        midpoint = 12,",
  "        na.value = \"gray90\",",
  "        name = \"FI Rate (%)\",",
  "        limits = c(5, 20)",
  "      ) +",
  "      coord_map(\"albers\", lat0 = 39, lat1 = 45) +",
  "      labs(",
  "        title = paste0(\"State-Level Food Insecurity (\", selected_year(), \")\")",
  "      ) +",
  "      theme_void() +",
  "      theme(",
  "        plot.title = element_text(face = \"bold\", size = 14, color = \"#1E3A5F\", hjust = 0.5),",
  "        legend.position = \"right\",",
  "        legend.title = element_text(face = \"bold\", size = 11),",
  "        plot.margin = margin(10, 10, 10, 10)",
  "      )",
  "  }, height = 400, res = 96)"
)

# Build new file
new_server <- c(
  server_code[1:(state_map_line - 1)],
  "",
  lookup_code,
  "",
  new_map_code,
  "",
  server_code[(end_line + 1):length(server_code)]
)

# Write the new file
writeLines(new_server, "R/server_overview.R")

cat("✅ server_overview.R updated successfully!\n")

EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "✅ STATE MAP FIX COMPLETE!"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "📋 What was fixed:"
    echo "  • Added state abbreviation → full name lookup table"
    echo "  • Updated state_map to use full state names"
    echo "  • Map will now display correctly with colors"
    echo ""
    echo "🚀 Next step:"
    echo "  Run your app: R --vanilla -e \"shiny::runApp('app.R')\""
    echo ""
    echo "📁 Backup saved as: R/server_overview_backup_*.R"
    echo ""
else
    echo ""
    echo "❌ Fix failed! Check the error messages above."
    echo "Your original file is safe - backup was created."
    echo ""
    exit 1
fi
