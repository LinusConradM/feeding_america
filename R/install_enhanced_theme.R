# ==============================================================================
# INSTALL ENHANCED PREMIUM THEME - COLORFUL CARDS
# ==============================================================================
# This script updates your premium theme with vibrant, colorful KPI cards
# ==============================================================================

cat("\n")
cat("========================================\n")
cat("ENHANCED PREMIUM THEME INSTALLER\n")
cat("========================================\n\n")

# Check if www folder exists
if (!dir.exists("www")) {
  cat("Creating www/ folder...\n")
  dir.create("www")
}

# Check if old theme exists
if (file.exists("www/premium_theme.css")) {
  cat("✓ Found existing premium_theme.css\n")
  cat("  Creating backup: premium_theme_backup.css\n")
  file.copy("www/premium_theme.css", "www/premium_theme_backup.css", overwrite = TRUE)
}

# Copy new enhanced theme
cat("\nInstalling enhanced theme...\n")
file.copy(
  "premium_theme_enhanced.css",
  "www/premium_theme.css",
  overwrite = TRUE
)

cat("✓ Enhanced theme installed!\n\n")

cat("========================================\n")
cat("WHAT'S NEW:\n")
cat("========================================\n")
cat("✨ Colorful gradient KPI cards:\n")
cat("   • Food Insecurity Rate → Coral gradient\n")
cat("   • Total Food Insecure → Navy gradient\n")
cat("   • Child FI Rate → Plum gradient\n")
cat("   • Cost Per Meal → Amber gradient\n")
cat("   • Poverty Rate → Blue gradient\n")
cat("   • Median Income → Green gradient\n")
cat("   • Unemployment → Coral gradient\n")
cat("   • Budget Shortfall → Navy gradient\n\n")

cat("🎨 Visual enhancements:\n")
cat("   • Smooth hover animations\n")
cat("   • Floating card effects\n")
cat("   • Subtle background patterns\n")
cat("   • Color-coded change indicators\n")
cat("   • Professional shadows & depth\n\n")

cat("📊 Plot improvements:\n")
cat("   • Rounded corners on charts\n")
cat("   • Hover effects for interactivity\n")
cat("   • Mint green accent borders\n")
cat("   • Enhanced data tables\n\n")

cat("========================================\n")
cat("NEXT STEPS:\n")
cat("========================================\n")
cat("1. Restart R session\n")
cat("2. Run: shiny::runApp()\n")
cat("3. Navigate to Executive Overview tab\n")
cat("4. Enjoy your colorful dashboard! 🎉\n\n")

cat("========================================\n")
cat("COLOR PALETTE:\n")
cat("========================================\n")
cat("🔵 Navy Deep:    #1E3A5F (primary)\n")
cat("🟠 Warm Amber:   #F4A261 (accents)\n")
cat("🟢 Fresh Mint:   #2A9D8F (success)\n")
cat("🟣 Deep Plum:    #9D4EDD (innovation)\n")
cat("🔴 Alert Coral:  #E63946 (warnings)\n")
cat("✅ Success:      #06D6A0 (positive)\n\n")

cat("========================================\n\n")

cat("Theme successfully installed! 🎨✨\n\n")
