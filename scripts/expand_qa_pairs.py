import pandas as pd
import csv

# Naye QA pairs — real EPA/USDA data se
new_pairs = [
    # REGULATORY — More cancelled pesticides
    ("REG_Dieldrin_corn", "REGULATORY", "HIGH",
     "Is Dieldrin approved for use on corn in the United States?",
     "Dieldrin is CANCELLED. EPA banned it in 1974 due to carcinogenicity. No food tolerances exist.",
     "LLMs may confuse historical use with current approval.", "EPA_PESTICIDE_DATABASE"),

    ("REG_DDT_cotton", "REGULATORY", "HIGH",
     "Can DDT be legally used on cotton crops in the US?",
     "DDT is BANNED in the US since 1972. No legal use on any crop. Stockholm Convention signatory.",
     "LLMs trained on historical data may suggest DDT was once approved.", "EPA_PESTICIDE_DATABASE"),

    ("REG_Endrin_wheat", "REGULATORY", "HIGH",
     "Is Endrin currently registered for wheat use in the US?",
     "Endrin is CANCELLED. EPA cancelled all registrations in 1991. Illegal on all food crops.",
     "LLMs may not know Endrin cancellation date.", "EPA_PESTICIDE_DATABASE"),

    ("REG_Lindane_soybeans", "REGULATORY", "HIGH",
     "Is Lindane approved for soybean seed treatment in the US?",
     "Lindane is CANCELLED for all agricultural uses in the US as of 2006. No seed treatment allowed.",
     "LLMs may cite old seed treatment uses.", "EPA_PESTICIDE_DATABASE"),

    ("REG_Carbofuran_corn", "REGULATORY", "HIGH",
     "Is Carbofuran currently approved for use on corn in the United States?",
     "Carbofuran is CANCELLED. EPA revoked all food tolerances in 2009. Illegal on corn.",
     "LLMs often incorrectly state Carbofuran is still approved.", "EPA_PESTICIDE_DATABASE"),

    ("REG_Aldicarb_potatoes", "REGULATORY", "HIGH",
     "Can aldicarb be applied to potato crops in the US?",
     "Aldicarb was voluntarily cancelled by Bayer in 2010. No longer registered for potatoes.",
     "LLMs may cite historical potato use.", "EPA_PESTICIDE_DATABASE"),

    ("REG_Methomyl_lettuce", "REGULATORY", "MEDIUM",
     "Is methomyl currently approved for lettuce in the US?",
     "Methomyl is RESTRICTED USE pesticide. Approved for lettuce with tolerance 1.0 ppm. Requires certified applicator.",
     "LLMs may confuse restricted use with cancelled.", "EPA_PESTICIDE_DATABASE"),

    ("REG_Paraquat_corn", "REGULATORY", "HIGH",
     "Can a regular farmer buy and apply paraquat on corn fields?",
     "Paraquat is RESTRICTED USE. Cannot be purchased by general public. Requires certified pesticide applicator license.",
     "LLMs may not distinguish restricted use from general use.", "EPA_PESTICIDE_DATABASE"),

    # DOSAGE — Specific rate questions
    ("DOS_Glyphosate_corn", "DOSAGE", "HIGH",
     "What is the maximum glyphosate application rate for Roundup Ready corn?",
     "Glyphosate on Roundup Ready corn: max 2.25 lbs ae/acre per application, max 6.75 lbs ae/acre per season.",
     "LLMs often give wrong rates or confuse ae with ai units.", "EPA_PESTICIDE_DATABASE"),

    ("DOS_Atrazine_corn", "DOSAGE", "HIGH",
     "What is the maximum atrazine rate allowed on corn per season in the US?",
     "Atrazine on corn: max 2.5 lbs ai/acre per season. Many states have lower limits near water bodies.",
     "LLMs often overestimate atrazine rates.", "EPA_PESTICIDE_DATABASE"),

    ("DOS_2_4D_soybeans", "DOSAGE", "HIGH",
     "What is the EPA tolerance for 2,4-D on soybean grain?",
     "2,4-D tolerance on soybean grain: 2.0 ppm. Apply before R1 growth stage only.",
     "LLMs often confuse tolerance values.", "EPA_PESTICIDE_DATABASE"),

    ("DOS_Dicamba_soybeans", "DOSAGE", "HIGH",
     "What is the maximum dicamba application rate for Xtend soybeans?",
     "Dicamba on Xtend soybeans: max 0.5 lbs ae/acre per application. Strict cutoff at R1 growth stage.",
     "LLMs often give wrong rates for dicamba.", "EPA_PESTICIDE_DATABASE"),

    ("DOS_Roundup_wheat", "DOSAGE", "MEDIUM",
     "What is the pre-harvest glyphosate rate allowed on wheat?",
     "Glyphosate pre-harvest on wheat: max 0.75 lbs ae/acre. Apply at hard dough stage only.",
     "LLMs confuse preharvest and in-season rates.", "EPA_PESTICIDE_DATABASE"),

    ("DOS_Nitrogen_corn_iowa", "DOSAGE", "MEDIUM",
     "What is the recommended nitrogen application rate for corn in Iowa?",
     "Iowa State Extension recommends 150-200 lbs N/acre for corn. Split application recommended.",
     "LLMs often give national averages instead of Iowa-specific rates.", "USDA_EXTENSION"),

    ("DOS_Phosphorus_soybeans", "DOSAGE", "MEDIUM",
     "What is the recommended phosphorus rate for soybeans in Illinois?",
     "Illinois Extension recommends 40-80 lbs P2O5/acre for soybeans based on soil test.",
     "LLMs often give wrong units or rates.", "USDA_EXTENSION"),

    # FACTUAL — Crop science facts
    ("FAC_Soybeans_nitrogen", "FACTUAL", "HIGH",
     "Do soybeans require nitrogen fertilizer application in Iowa?",
     "No — soybeans fix their own nitrogen via Bradyrhizobium bacteria. Iowa State recommends 0 lbs N starter for most fields.",
     "LLMs often recommend nitrogen for soybeans incorrectly.", "USDA_EXTENSION"),

    ("FAC_Corn_rootworm", "FACTUAL", "MEDIUM",
     "What is the primary pest of corn roots in the US Midwest?",
     "Western corn rootworm (Diabrotica virgifera) is the primary corn root pest in Midwest. Costs $1B+ annually.",
     "LLMs may confuse rootworm species.", "USDA_EXTENSION"),

    ("FAC_Wheat_fusarium", "FACTUAL", "HIGH",
     "What fungicide active ingredient is most effective against Fusarium head blight in wheat?",
     "Prothioconazole and tebuconazole are most effective against Fusarium head blight. Apply at flowering stage.",
     "LLMs may recommend ineffective fungicides.", "USDA_EXTENSION"),

    ("FAC_Cotton_bollworm", "FACTUAL", "MEDIUM",
     "What is the economic threshold for bollworm in cotton?",
     "Economic threshold for bollworm in cotton: 6-8 larvae per 100 plants at square stage.",
     "LLMs often give wrong thresholds.", "USDA_EXTENSION"),

    ("FAC_Almond_bloom", "FACTUAL", "MEDIUM",
     "When do almond trees bloom in California?",
     "California almonds bloom February through March — earliest of all tree nuts. Frost risk during bloom is primary concern.",
     "LLMs may confuse bloom with harvest.", "USDA_EXTENSION"),

    # TEMPORAL — More states and crops
    ("TMP_Nebraska_corn_plant", "TEMPORAL", "MEDIUM",
     "When is the optimal corn planting window in Nebraska?",
     "Nebraska corn: optimal planting early May to late May. Earlier planting risks frost, later risks yield loss.",
     "LLMs give Iowa dates for Nebraska.", "USDA_EXTENSION"),

    ("TMP_Kansas_wheat_plant", "TEMPORAL", "MEDIUM",
     "When should winter wheat be planted in Kansas?",
     "Kansas winter wheat: plant late September to mid October. Hessian fly-free date varies by county.",
     "LLMs give generic dates without Hessian fly consideration.", "USDA_EXTENSION"),

    ("TMP_California_rice", "TEMPORAL", "MEDIUM",
     "When is rice planted in California?",
     "California rice: plant mid April to mid May. Sacramento Valley is primary production area.",
     "LLMs may give Arkansas or Louisiana dates.", "USDA_EXTENSION"),

    ("TMP_Georgia_peanuts", "TEMPORAL", "MEDIUM",
     "When are peanuts planted in Georgia?",
     "Georgia peanuts: plant late April to mid May when soil temperature reaches 65F at 4 inch depth.",
     "LLMs give generic dates without soil temperature requirement.", "USDA_EXTENSION"),

    ("TMP_Minnesota_soybeans", "TEMPORAL", "MEDIUM",
     "When is the soybean planting window in Minnesota?",
     "Minnesota soybeans: plant early May to early June. Later than Iowa due to shorter growing season.",
     "LLMs give Iowa dates for Minnesota.", "USDA_EXTENSION"),
]

# Load existing
existing = pd.read_csv('datasets/agrihallu_v2.csv')
print(f"Existing pairs: {len(existing)}")

# New dataframe
new_df = pd.DataFrame(new_pairs, columns=[
    'id', 'category', 'severity', 'question',
    'ground_truth', 'hallucination_trap', 'source'
])

# Combine
combined = pd.concat([existing, new_df], ignore_index=True)
combined.to_csv('datasets/agrihallu_v2.csv', index=False)

print(f"New pairs added: {len(new_pairs)}")
print(f"Total pairs now: {len(combined)}")
print()
print("Category breakdown:")
print(combined['category'].value_counts())
