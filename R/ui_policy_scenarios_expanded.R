# ==============================================================================
# UI MODULE: POLICY SCENARIO & SIMULATION
# ==============================================================================
# PURPOSE: Support decision-making with what-if analysis
# CAPABILITIES: Interactive sliders, model projections, scenario comparison
# TEAM: Conrad, Sharon, Ryann, Alex
# ==============================================================================

ui_policy_scenarios <- tabPanel(
  "Policy Scenarios",
  value = "scenarios",
  
  fluidPage(
    # Global Controls
    # global_controls_ui(),  # Removed to prevent duplicate IDs
    
    # Page Header
    fluidRow(
      column(
        12,
        h2(
          icon("sliders-h"), " Policy Scenario & Simulation Tool",
          style = "color: #2c3e50; font-weight: 600; margin-bottom: 10px;"
        ),
        p(
          "Model the impact of policy interventions on food insecurity rates",
          style = "color: #6c757d; font-size: 16px; margin-bottom: 30px;"
        )
      )
    ),
    
    # ========================================================================
    # SCENARIO BUILDER
    # ========================================================================
    fluidRow(
      column(
        4,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4("Scenario Parameters", style = "margin-top: 0; color: #2c3e50;"),
          p("Adjust policy levers to see projected impact on food insecurity",
            style = "color: #6c757d; font-size: 14px; margin-bottom: 20px;"),
          hr(),
          
          # Poverty reduction scenario
          h5(icon("usd"), " Economic Interventions", 
             style = "color: #0033A0; margin-top: 20px;"),
          
          sliderInput(
            "poverty_reduction",
            "Poverty Rate Reduction (%)",
            min = 0,
            max = 50,
            value = 0,
            step = 5,
            post = "%"
          ),
          
          sliderInput(
            "income_increase",
            "Median Income Growth (%)",
            min = 0,
            max = 30,
            value = 0,
            step = 2.5,
            post = "%"
          ),
          
          sliderInput(
            "unemployment_decrease",
            "Unemployment Reduction (%)",
            min = 0,
            max = 50,
            value = 0,
            step = 5,
            post = "%"
          ),
          
          hr(),
          
          # SNAP expansion
          h5(icon("utensils"), " SNAP Expansion", 
             style = "color: #28a745; margin-top: 20px;"),
          
          sliderInput(
            "snap_expansion",
            "SNAP Participation Increase (%)",
            min = 0,
            max = 100,
            value = 0,
            step = 10,
            post = "%"
          ),
          
          sliderInput(
            "snap_benefit_increase",
            "SNAP Benefit Level Increase (%)",
            min = 0,
            max = 50,
            value = 0,
            step = 5,
            post = "%"
          ),
          
          hr(),
          
          # Additional interventions
          h5(icon("heartbeat"), " Health & Education", 
             style = "color: #C41E3A; margin-top: 20px;"),
          
          sliderInput(
            "insurance_expansion",
            "Health Insurance Coverage Increase (%)",
            min = 0,
            max = 100,
            value = 0,
            step = 10,
            post = "%"
          ),
          
          hr(),
          
          fluidRow(
            column(
              6,
              actionButton(
                "run_scenario",
                "Run Scenario",
#                 icon removed for debugging
                style = "width: 100%; background: #0033A0; color: white; 
                         border: none; padding: 12px; font-weight: 600;"
              )
            ),
            column(
              6,
              actionButton(
                "reset_scenario",
                "Reset",
#                 icon removed for debugging
                style = "width: 100%; background: #6c757d; color: white; 
                         border: none; padding: 12px;"
              )
            )
          )
        )
      ),
      
      # ========================================================================
      # SCENARIO RESULTS
      # ========================================================================
      column(
        8,
        # Impact Summary Cards
        fluidRow(
          column(
            4,
            div(
              style = "background: linear-gradient(135deg, #0033A0 0%, #003D82 100%);
                       padding: 25px; border-radius: 10px; color: white;
                       box-shadow: 0 4px 15px rgba(0, 51, 160, 0.3);
                       margin-bottom: 20px;",
              h6("Baseline FI Rate", style = "margin: 0 0 10px 0; opacity: 0.9;"),
              h2(textOutput("baseline_fi"), style = "margin: 0; font-size: 48px;"),
              p("Current national average", 
                style = "margin-top: 10px; font-size: 13px; opacity: 0.8;")
            )
          ),
          
          column(
            4,
            div(
              style = "background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                       padding: 25px; border-radius: 10px; color: white;
                       box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
                       margin-bottom: 20px;",
              h6("Projected FI Rate", style = "margin: 0 0 10px 0; opacity: 0.9;"),
              h2(textOutput("projected_fi"), style = "margin: 0; font-size: 48px;"),
              p("After interventions", 
                style = "margin-top: 10px; font-size: 13px; opacity: 0.8;")
            )
          ),
          
          column(
            4,
            div(
              style = "background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
                       padding: 25px; border-radius: 10px; color: white;
                       box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
                       margin-bottom: 20px;",
              h6("Reduction", style = "margin: 0 0 10px 0; opacity: 0.9;"),
              h2(textOutput("fi_reduction"), style = "margin: 0; font-size: 48px;"),
              p("Percentage points", 
                style = "margin-top: 10px; font-size: 13px; opacity: 0.8;")
            )
          )
        ),
        
        # Projected Impact Visualization
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px;",
          h4(
            icon("chart-bar"), " Projected Impact by Intervention",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          # Impact chart placeholder
          div(
            style = "height: 350px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("chart-bar", style = "font-size: 60px; color: #0033A0; margin-bottom: 20px;"),
              h4("Waterfall Chart of Policy Impacts", 
                 style = "color: #495057; margin-bottom: 10px;"),
              p("Shows contribution of each intervention to total reduction",
                style = "color: #6c757d;")
            )
          )
        ),
        
        # People Lifted Out of Food Insecurity
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("users"), " Population Impact",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          hr(),
          
          fluidRow(
            column(
              6,
              div(
                style = "background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;",
                h3(textOutput("people_helped"), 
                   style = "font-size: 48px; color: #28a745; margin: 15px 0;"),
                p("People lifted out of food insecurity",
                  style = "color: #6c757d; font-size: 15px;")
              )
            ),
            
            column(
              6,
              div(
                style = "background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;",
                h3(textOutput("cost_estimate"), 
                   style = "font-size: 48px; color: #0033A0; margin: 15px 0;"),
                p("Estimated annual cost (billion $)",
                  style = "color: #6c757d; font-size: 15px;")
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # SCENARIO COMPARISON TABLE
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08);",
          h4(
            icon("table"), " Scenario Comparison",
            style = "margin-top: 0; color: #2c3e50;"
          ),
          p("Compare different policy combinations side-by-side",
            style = "color: #6c757d; margin-bottom: 20px;"),
          hr(),
          
          # Comparison table placeholder
          div(
            style = "min-height: 300px; display: flex; align-items: center; 
                     justify-content: center; background: #f8f9fa; 
                     border-radius: 8px; border: 2px dashed #dee2e6;",
            div(
              style = "text-align: center;",
              icon("table", style = "font-size: 50px; color: #17a2b8; margin-bottom: 15px;"),
              h5("Save and Compare Multiple Scenarios", style = "color: #495057;"),
              p("Table showing baseline vs. multiple intervention scenarios", 
                style = "color: #6c757d; font-size: 13px;")
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # EXPORT SCENARIO SUMMARY
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: white; padding: 25px; border-radius: 10px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;",
          h4("Export Scenario for Policy Memo", style = "margin-top: 0; color: #2c3e50;"),
          p("Download scenario parameters and results for inclusion in reports",
            style = "color: #6c757d; margin-bottom: 20px;"),
          
          fluidRow(
            column(
              4,
              actionButton(
                "export_pdf",
                "Export as PDF",
#                 icon removed for debugging
                style = "width: 100%; padding: 12px;"
              )
            ),
            column(
              4,
              actionButton(
                "export_csv",
                "Export as CSV",
#                 icon removed for debugging
                style = "width: 100%; padding: 12px;"
              )
            ),
            column(
              4,
              actionButton(
                "export_ppt",
                "Export to PowerPoint",
#                 icon removed for debugging
                style = "width: 100%; padding: 12px;"
              )
            )
          )
        )
      )
    ),
    
    # ========================================================================
    # MODEL ASSUMPTIONS & LIMITATIONS
    # ========================================================================
    fluidRow(
      style = "margin-top: 30px;",
      column(
        12,
        div(
          style = "background: #fff3cd; padding: 20px; border-radius: 10px;
                   border-left: 6px solid #ffc107;",
          h5(icon("exclamation-triangle"), " Model Assumptions & Limitations", 
             style = "color: #856404; margin-top: 0;"),
          p("Projections are based on historical regression coefficients and assume linear relationships. 
            Actual impacts may vary due to implementation challenges, behavioral responses, and 
            macroeconomic factors not captured in the model. These scenarios should inform—not 
            replace—comprehensive policy analysis.",
            style = "color: #856404; font-size: 14px; line-height: 1.6; margin: 0;")
        )
      )
    )
  )
)
