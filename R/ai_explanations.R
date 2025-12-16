# ==============================================================================
# AI EXPLANATION MODULE - ANTHROPIC CLAUDE API
# ==============================================================================
# Adds intelligent, natural language explanations to your dashboard
# ==============================================================================

# ==============================================================================
# REQUIRED PACKAGES
# ==============================================================================

if (!require("httr")) install.packages("httr")
if (!require("jsonlite")) install.packages("jsonlite")

library(httr)
library(jsonlite)

# ==============================================================================
# API CONFIGURATION
# ==============================================================================

# Store your API key in .Renviron file:
# ANTHROPIC_API_KEY="your-api-key-here"
# 
# Or set it directly (NOT recommended for production):
# Sys.setenv(ANTHROPIC_API_KEY = "your-api-key")

get_api_key <- function() {
  api_key <- Sys.getenv("ANTHROPIC_API_KEY")
  
  if (api_key == "") {
    stop(
      "Anthropic API key not found!\n",
      "Please set ANTHROPIC_API_KEY in your .Renviron file or environment.\n",
      "Get your API key at: https://console.anthropic.com/"
    )
  }
  
  return(api_key)
}

# ==============================================================================
# CORE API FUNCTION
# ==============================================================================

#' Call Claude API for Explanations
#'
#' @param prompt Character string with the explanation request
#' @param context Optional data context (data summary, stats, etc.)
#' @param max_tokens Maximum tokens in response (default: 500)
#' @param temperature Creativity level 0-1 (default: 0.3 for factual)
#' @param model Claude model to use (default: claude-sonnet-4-20250514)
#'
#' @return Character string with Claude's explanation
#'
#' @export
ask_claude <- function(prompt, 
                       context = NULL, 
                       max_tokens = 500,
                       temperature = 0.3,
                       model = "claude-sonnet-4-20250514") {
  
  # Get API key
  api_key <- get_api_key()
  
  # Build full prompt with context
  full_prompt <- prompt
  if (!is.null(context)) {
    full_prompt <- paste0(
      "Context:\n", context, "\n\n",
      "Question:\n", prompt
    )
  }
  
  # API request
  response <- tryCatch({
    POST(
      url = "https://api.anthropic.com/v1/messages",
      add_headers(
        "x-api-key" = api_key,
        "anthropic-version" = "2023-06-01",
        "content-type" = "application/json"
      ),
      body = toJSON(list(
        model = model,
        max_tokens = max_tokens,
        temperature = temperature,
        messages = list(
          list(
            role = "user",
            content = full_prompt
          )
        )
      ), auto_unbox = TRUE),
      encode = "json"
    )
  }, error = function(e) {
    stop("API request failed: ", e$message)
  })
  
  # Check for errors
  if (status_code(response) != 200) {
    error_content <- content(response, "text", encoding = "UTF-8")
    stop("API error (", status_code(response), "): ", error_content)
  }
  
  # Parse response
  result <- content(response, "parsed")
  explanation <- result$content[[1]]$text
  
  return(explanation)
}

# ==============================================================================
# SPECIALIZED EXPLANATION FUNCTIONS
# ==============================================================================

#' Explain a Time Series Plot
#'
#' @param data Data frame with time series data
#' @param x_var Name of time variable
#' @param y_var Name of value variable
#' @param title Plot title
#'
#' @return HTML-formatted explanation
#'
#' @export
explain_time_series <- function(data, x_var, y_var, title = NULL) {
  
  # Calculate key statistics
  trend_direction <- if (cor(as.numeric(data[[x_var]]), data[[y_var]], 
                             use = "complete.obs") > 0) "upward" else "downward"
  
  start_val <- round(data[[y_var]][1], 2)
  end_val <- round(data[[y_var]][nrow(data)], 2)
  change <- round(end_val - start_val, 2)
  pct_change <- round((change / start_val) * 100, 1)
  
  max_val <- max(data[[y_var]], na.rm = TRUE)
  min_val <- min(data[[y_var]], na.rm = TRUE)
  max_year <- data[[x_var]][which.max(data[[y_var]])]
  min_year <- data[[x_var]][which.min(data[[y_var]])]
  
  # Build context
  context <- paste0(
    "Time series data analysis:\n",
    "- Variable: ", y_var, "\n",
    "- Time period: ", min(data[[x_var]]), " to ", max(data[[x_var]]), "\n",
    "- Overall trend: ", trend_direction, "\n",
    "- Starting value: ", start_val, "\n",
    "- Ending value: ", end_val, "\n",
    "- Total change: ", change, " (", pct_change, "%)\n",
    "- Highest value: ", round(max_val, 2), " in ", max_year, "\n",
    "- Lowest value: ", round(min_val, 2), " in ", min_year
  )
  
  # Prompt
  prompt <- paste0(
    "Explain this time series chart in 2-3 clear sentences. ",
    "Focus on the key trends, notable peaks/valleys, and what they might mean for food insecurity. ",
    "Write for a general audience (policymakers, students, journalists). ",
    "Be concise and avoid jargon.",
    if (!is.null(title)) paste0("\n\nChart title: ", title) else ""
  )
  
  # Get explanation
  explanation <- ask_claude(prompt, context, max_tokens = 300, temperature = 0.2)
  
  # Format as HTML
  html_output <- HTML(paste0(
    '<div class="ai-explanation" style="',
    'background: linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%); ',
    'border-left: 4px solid #2A9D8F; ',
    'padding: 16px 20px; ',
    'border-radius: 8px; ',
    'margin-top: 16px; ',
    'box-shadow: 0 2px 8px rgba(0,0,0,0.08);">',
    '<div style="display: flex; align-items: center; margin-bottom: 8px;">',
    '<span style="font-size: 20px; margin-right: 8px;">🤖</span>',
    '<strong style="color: #1E3A5F;">AI Insight</strong>',
    '</div>',
    '<p style="margin: 0; color: #2D3142; line-height: 1.6;">',
    explanation,
    '</p>',
    '</div>'
  ))
  
  return(html_output)
}

#' Explain Statistical Results
#'
#' @param stats Named list of statistics (e.g., mean, median, correlation, etc.)
#' @param context_description Brief description of what's being analyzed
#'
#' @return HTML-formatted explanation
#'
#' @export
explain_statistics <- function(stats, context_description) {
  
  # Build context
  stats_text <- paste(names(stats), "=", round(unlist(stats), 3), collapse = ", ")
  
  context <- paste0(
    "Statistical analysis context: ", context_description, "\n",
    "Key statistics: ", stats_text
  )
  
  prompt <- paste0(
    "Explain what these statistics mean in plain language. ",
    "Focus on practical implications for understanding food insecurity patterns. ",
    "Use accessible language and provide actionable insights. ",
    "Keep it to 2-3 sentences."
  )
  
  explanation <- ask_claude(prompt, context, max_tokens = 300, temperature = 0.2)
  
  # Format as HTML
  html_output <- HTML(paste0(
    '<div class="ai-explanation" style="',
    'background: linear-gradient(135deg, #FFF8F0 0%, #FFFFFF 100%); ',
    'border-left: 4px solid #F4A261; ',
    'padding: 16px 20px; ',
    'border-radius: 8px; ',
    'margin-top: 16px;">',
    '<div style="display: flex; align-items: center; margin-bottom: 8px;">',
    '<span style="font-size: 20px; margin-right: 8px;">💡</span>',
    '<strong style="color: #1E3A5F;">Key Insight</strong>',
    '</div>',
    '<p style="margin: 0; color: #2D3142; line-height: 1.6;">',
    explanation,
    '</p>',
    '</div>'
  ))
  
  return(html_output)
}

#' Explain Comparison Between Groups
#'
#' @param group1_name Name of first group
#' @param group1_value Metric value for first group
#' @param group2_name Name of second group
#' @param group2_value Metric value for second group
#' @param metric_name Name of the metric being compared
#'
#' @return HTML-formatted explanation
#'
#' @export
explain_comparison <- function(group1_name, group1_value, 
                               group2_name, group2_value, 
                               metric_name) {
  
  difference <- group1_value - group2_value
  pct_diff <- abs((difference / group2_value) * 100)
  higher_group <- if (group1_value > group2_value) group1_name else group2_name
  
  context <- paste0(
    "Comparison analysis:\n",
    "- Metric: ", metric_name, "\n",
    "- ", group1_name, ": ", round(group1_value, 2), "\n",
    "- ", group2_name, ": ", round(group2_value, 2), "\n",
    "- Difference: ", round(difference, 2), " (", round(pct_diff, 1), "%)\n",
    "- Higher in: ", higher_group
  )
  
  prompt <- paste0(
    "Explain what this comparison reveals about food insecurity disparities. ",
    "What might explain this difference? What are the policy implications? ",
    "Write 2-3 clear sentences for a general audience."
  )
  
  explanation <- ask_claude(prompt, context, max_tokens = 300, temperature = 0.3)
  
  html_output <- HTML(paste0(
    '<div class="ai-explanation" style="',
    'background: linear-gradient(135deg, #F0F4FF 0%, #FFFFFF 100%); ',
    'border-left: 4px solid #9D4EDD; ',
    'padding: 16px 20px; ',
    'border-radius: 8px; ',
    'margin-top: 16px;">',
    '<div style="display: flex; align-items: center; margin-bottom: 8px;">',
    '<span style="font-size: 20px; margin-right: 8px;">⚖️</span>',
    '<strong style="color: #1E3A5F;">Disparity Analysis</strong>',
    '</div>',
    '<p style="margin: 0; color: #2D3142; line-height: 1.6;">',
    explanation,
    '</p>',
    '</div>'
  ))
  
  return(html_output)
}

#' Answer Custom Question About Data
#'
#' @param question User's question
#' @param data_summary Summary of relevant data
#'
#' @return HTML-formatted answer
#'
#' @export
answer_question <- function(question, data_summary) {
  
  context <- paste0(
    "Data context for food insecurity analytics dashboard:\n",
    data_summary
  )
  
  prompt <- paste0(
    "User question: ", question, "\n\n",
    "Provide a clear, accurate answer based on the data. ",
    "If you're not certain, say so. Be helpful and actionable. ",
    "Keep the answer to 2-4 sentences."
  )
  
  answer <- ask_claude(prompt, context, max_tokens = 400, temperature = 0.4)
  
  html_output <- HTML(paste0(
    '<div class="ai-explanation" style="',
    'background: #FFFFFF; ',
    'border: 2px solid #2A9D8F; ',
    'padding: 16px 20px; ',
    'border-radius: 8px; ',
    'margin-top: 16px; ',
    'box-shadow: 0 2px 8px rgba(0,0,0,0.08);">',
    '<div style="display: flex; align-items: center; margin-bottom: 8px;">',
    '<span style="font-size: 20px; margin-right: 8px;">💬</span>',
    '<strong style="color: #1E3A5F;">AI Response</strong>',
    '</div>',
    '<p style="margin: 0; color: #2D3142; line-height: 1.6;">',
    answer,
    '</p>',
    '</div>'
  ))
  
  return(html_output)
}

# ==============================================================================
# CACHING SYSTEM (Optional - for performance)
# ==============================================================================

# Simple in-memory cache to avoid regenerating identical explanations
explanation_cache <- new.env()

#' Cached version of ask_claude
#'
#' @inheritParams ask_claude
#' @param use_cache Whether to use caching (default: TRUE)
#'
#' @return Character string with explanation
#'
#' @export
ask_claude_cached <- function(prompt, context = NULL, max_tokens = 500,
                              temperature = 0.3, model = "claude-sonnet-4-20250514",
                              use_cache = TRUE) {
  
  if (!use_cache) {
    return(ask_claude(prompt, context, max_tokens, temperature, model))
  }
  
  # Create cache key
  cache_key <- digest::digest(list(prompt, context, max_tokens, temperature, model))
  
  # Check cache
  if (exists(cache_key, envir = explanation_cache)) {
    return(get(cache_key, envir = explanation_cache))
  }
  
  # Generate new explanation
  explanation <- ask_claude(prompt, context, max_tokens, temperature, model)
  
  # Store in cache
  assign(cache_key, explanation, envir = explanation_cache)
  
  return(explanation)
}

#' Clear explanation cache
#'
#' @export
clear_explanation_cache <- function() {
  rm(list = ls(envir = explanation_cache), envir = explanation_cache)
  message("Explanation cache cleared")
}

# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if (FALSE) {
  # Example 1: Explain time series
  trend_data <- data.frame(
    year = 2009:2023,
    food_insecurity_rate = c(14.6, 14.5, 14.9, 14.5, 14.3, 14.0, 
                             13.1, 12.3, 11.8, 10.9, 10.5, 13.9, 
                             10.2, 10.5, 11.3)
  )
  
  explanation <- explain_time_series(
    data = trend_data,
    x_var = "year",
    y_var = "food_insecurity_rate",
    title = "National Food Insecurity Rate (2009-2023)"
  )
  
  # Example 2: Explain statistics
  stats <- list(
    correlation = 0.87,
    p_value = 0.001,
    n = 3142
  )
  
  explanation <- explain_statistics(
    stats = stats,
    context_description = "Correlation between poverty rate and food insecurity rate across U.S. counties"
  )
  
  # Example 3: Compare groups
  explanation <- explain_comparison(
    group1_name = "Rural Counties",
    group1_value = 15.2,
    group2_name = "Urban Counties",
    group2_value = 12.1,
    metric_name = "Food Insecurity Rate (%)"
  )
  
  # Example 4: Answer question
  data_summary <- "Dataset contains 3,142 U.S. counties from 2009-2023 with food insecurity rates, poverty rates, median income, and demographic data."
  
  answer <- answer_question(
    question = "Which counties improved the most from 2009 to 2023?",
    data_summary = data_summary
  )
}

# ==============================================================================
# SETUP INSTRUCTIONS
# ==============================================================================

cat("\n")
cat("========================================\n")
cat("AI EXPLANATION MODULE LOADED\n")
cat("========================================\n\n")

cat("Setup steps:\n")
cat("1. Get API key from https://console.anthropic.com/\n")
cat("2. Add to .Renviron: ANTHROPIC_API_KEY=\"your-key\"\n")
cat("3. Restart R session\n")
cat("4. Test with: ask_claude('Explain food insecurity')\n\n")

cat("Available functions:\n")
cat("  • ask_claude() - General purpose\n")
cat("  • explain_time_series() - For trend charts\n")
cat("  • explain_statistics() - For statistical results\n")
cat("  • explain_comparison() - For group comparisons\n")
cat("  • answer_question() - For user Q&A\n\n")

cat("========================================\n\n")



# ==============================================================================
# AI EXPLANATIONS MODULE
# ==============================================================================
# PURPOSE: Provide AI-powered explanations using Claude API
# USAGE: source("R/ai_explanations.R") in global.R
# ==============================================================================

#' Call Claude API for AI-Generated Explanations
#'
#' @param prompt Character string containing the prompt to send to Claude
#' @param max_tokens Maximum tokens for response (default: 2000)
#' @return Character string with Claude's response
#' @export
ask_claude <- function(prompt, max_tokens = 2000) {
  
  tryCatch({
    
    # Check if API key is available
    api_key <- Sys.getenv("ANTHROPIC_API_KEY")
    
    if (api_key == "" || is.null(api_key)) {
      return(paste0(
        "<div style='background: #FFF3CD; border-left: 4px solid #FFC107; padding: 20px; border-radius: 8px;'>",
        "<h4 style='color: #856404; margin-top: 0;'>⚠️ API Key Not Found</h4>",
        "<p style='color: #856404; margin: 0;'>",
        "To enable AI-generated summaries, set your Anthropic API key:<br><br>",
        "<strong>In R Console:</strong><br>",
        "<code>Sys.setenv(ANTHROPIC_API_KEY = 'your-key-here')</code><br><br>",
        "<strong>Or in .Renviron file:</strong><br>",
        "<code>ANTHROPIC_API_KEY=your-key-here</code><br><br>",
        "Get your key from <a href='https://console.anthropic.com/' target='_blank'>console.anthropic.com</a>",
        "</p>",
        "</div>"
      ))
    }
    
    # Make API request
    response <- httr::POST(
      url = "https://api.anthropic.com/v1/messages",
      httr::add_headers(
        "x-api-key" = api_key,
        "anthropic-version" = "2023-06-01",
        "content-type" = "application/json"
      ),
      body = jsonlite::toJSON(list(
        model = "claude-sonnet-4-20250514",
        max_tokens = max_tokens,
        messages = list(
          list(
            role = "user",
            content = prompt
          )
        )
      ), auto_unbox = TRUE),
      encode = "json"
    )
    
    # Check for errors
    if (httr::http_error(response)) {
      error_content <- httr::content(response, as = "text", encoding = "UTF-8")
      
      return(paste0(
        "<div style='background: #F8D7DA; border-left: 4px solid #DC3545; padding: 20px; border-radius: 8px;'>",
        "<h4 style='color: #721C24; margin-top: 0;'>❌ API Error</h4>",
        "<p style='color: #721C24;'>Status: ", httr::status_code(response), "<br>",
        "Error: ", error_content, "</p>",
        "</div>"
      ))
    }
    
    # Parse response
    result <- httr::content(response, as = "parsed", encoding = "UTF-8")
    
    # Extract text
    if (!is.null(result$content) && length(result$content) > 0) {
      ai_text <- result$content[[1]]$text
      
      # Format as HTML
      return(paste0(
        "<div style='background: white; color: #2c3e50; padding: 25px; border-radius: 8px; line-height: 1.8;'>",
        gsub("\n\n", "</p><p>", gsub("\n", "<br>", ai_text)),
        "</div>"
      ))
      
    } else {
      return("<div style='padding: 20px;'><p>No response generated.</p></div>")
    }
    
  }, error = function(e) {
    return(paste0(
      "<div style='background: #F8D7DA; border-left: 4px solid #DC3545; padding: 20px; border-radius: 8px;'>",
      "<h4 style='color: #721C24; margin-top: 0;'>❌ Error</h4>",
      "<p style='color: #721C24;'>", as.character(e$message), "</p>",
      "</div>"
    ))
  })
}


#' Generate Spatial Intelligence Summary
#'
#' @export
generate_spatial_summary <- function(year, hotspots, coldspots, morans_i, disparity, max_fi, min_fi) {
  
  prompt <- paste0(
    "You are a spatial analyst providing insights on U.S. food insecurity for ", year, ". ",
    "Write a comprehensive, policy-focused analysis based on these spatial statistics:\n\n",
    "STATISTICS:\n",
    "• Hot-Spot Counties: ", hotspots, " (high-FI counties surrounded by high-FI counties, p<0.05)\n",
    "• Cold-Spot Counties: ", coldspots, " (low-FI counties surrounded by low-FI counties, p<0.05)\n",
    "• Moran's I: ", sprintf("%.3f", morans_i), " (spatial autocorrelation, 0=random, 1=clustered)\n",
    "• Geographic Disparity: ", disparity, "% (range: ", sprintf("%.1f%%", min_fi), " to ", sprintf("%.1f%%", max_fi), ")\n\n",
    "Please structure your analysis with these HTML-formatted sections:\n\n",
    "<h4 style='color: #0033A0;'>📍 Overview</h4>\n",
    "Brief introduction to what these patterns reveal\n\n",
    "<h4 style='color: #E63946;'>🔥 Hot-Spot Analysis</h4>\n",
    "Explain what ", hotspots, " hot-spots means and implications\n\n",
    "<h4 style='color: #28a745;'>✅ Cold-Spot Insights</h4>\n",
    "Discuss ", coldspots, " cold-spots and what we can learn\n\n",
    "<h4 style='color: #ffc107;'>📊 Clustering (Moran's I = ", sprintf("%.3f", morans_i), ")</h4>\n",
    "Interpret spatial autocorrelation strength\n\n",
    "<h4 style='color: #6f42c1;'>📏 Geographic Inequality</h4>\n",
    "Discuss ", disparity, "% disparity implications\n\n",
    "<h4 style='color: #0033A0;'>💡 Recommendations</h4>\n",
    "Provide 3-5 specific, actionable policy recommendations\n\n",
    "Use <p> tags for paragraphs. Be data-driven, policy-focused, and explain technical concepts clearly."
  )
  
  ask_claude(prompt, max_tokens = 3000)
}

# Load required packages
if (!require("httr", quietly = TRUE)) install.packages("httr")
if (!require("jsonlite", quietly = TRUE)) install.packages("jsonlite")

message("✓ AI Explanations module loaded!")