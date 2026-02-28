// Neo4j Knowledge Graph Seed Data
// Strategy Review PoC — Global Fund / International Development domain
//
// Node types: Document, Theme, Indicator, Country, FundingArea
// Relationship types: COVERS_THEME, MEASURED_BY, PRIORITY_IN, ALLOCATES_TO, SUPPORTS_THEME
//
// Run with: bash seed.sh

// Clear existing data (idempotent)
MATCH (n) DETACH DELETE n;

// Create all nodes and relationships in a single transaction
CREATE

// --- Documents ---
(doc_gh:Document {
  id: 'GH_2024',
  title: 'Global Health Strategy 2024-2028',
  type: 'Strategy',
  year: 2024,
  organization: 'Global Fund',
  region: 'Global'
}),
(doc_tb:Document {
  id: 'TB_2025',
  title: 'TB Elimination Plan 2025-2030',
  type: 'Strategy',
  year: 2025,
  organization: 'WHO',
  region: 'Global'
}),
(doc_ge:Document {
  id: 'GE_2023',
  title: 'Gender & Health Equity Framework 2023-2028',
  type: 'Framework',
  year: 2023,
  organization: 'Global Fund',
  region: 'Global'
}),

// --- Themes ---
(t_mnh:Theme {
  id: 'MNH',
  name: 'Maternal & Newborn Health',
  description: 'Reducing maternal and neonatal mortality through improved care access',
  priority: 'high'
}),
(t_hiv:Theme {
  id: 'HIV',
  name: 'HIV/AIDS Treatment & Prevention',
  description: 'Expanding antiretroviral access and prevention programs',
  priority: 'high'
}),
(t_malaria:Theme {
  id: 'MALARIA',
  name: 'Malaria Prevention & Control',
  description: 'Scaling bed nets, indoor spraying, and rapid diagnostics',
  priority: 'high'
}),
(t_tb:Theme {
  id: 'TB',
  name: 'Tuberculosis Elimination',
  description: 'Improving TB detection, treatment completion, and drug-resistant TB response',
  priority: 'high'
}),
(t_vaccine:Theme {
  id: 'VACCINE',
  name: 'Vaccine Delivery',
  description: 'Strengthening immunisation supply chains and coverage',
  priority: 'high'
}),
(t_digital:Theme {
  id: 'DIGITAL',
  name: 'Digital Health Innovation',
  description: 'Leveraging technology for health data systems and telemedicine',
  priority: 'medium'
}),
(t_gender:Theme {
  id: 'GENDER',
  name: 'Gender Equality & Womens Health',
  description: 'Addressing gender barriers to health access and outcomes',
  priority: 'high'
}),

// --- Indicators ---
(i_mmr:Indicator {
  id: 'MMR',
  name: 'Maternal Mortality Ratio',
  unit: 'per 100k live births',
  target: 70
}),
(i_nmr:Indicator {
  id: 'NMR',
  name: 'Neonatal Mortality Rate',
  unit: 'per 1000 live births',
  target: 12
}),
(i_art:Indicator {
  id: 'ART',
  name: 'HIV Treatment Coverage (ART)',
  unit: '%',
  target: 95
}),
(i_malaria_inc:Indicator {
  id: 'MALARIA_INCIDENCE',
  name: 'Malaria Case Incidence',
  unit: 'per 1000 population',
  target: 25
}),
(i_tb_success:Indicator {
  id: 'TB_SUCCESS',
  name: 'TB Treatment Success Rate',
  unit: '%',
  target: 90
}),
(i_dtp3:Indicator {
  id: 'DTP3',
  name: 'DTP3 Vaccination Coverage',
  unit: '%',
  target: 90
}),
(i_mcv1:Indicator {
  id: 'MCV1',
  name: 'Measles Vaccination Coverage',
  unit: '%',
  target: 95
}),
(i_gdi:Indicator {
  id: 'GDI',
  name: 'Gender Development Index',
  unit: 'index',
  target: 1.0
}),
(i_dhi:Indicator {
  id: 'DHI',
  name: 'Digital Health Index',
  unit: 'score 0-100',
  target: 75
}),
(i_facility:Indicator {
  id: 'FACILITY',
  name: 'Health Facility Density',
  unit: 'per 10k population',
  target: 2.0
}),

// --- Countries ---
(c_nga:Country {
  code: 'NGA',
  name: 'Nigeria',
  region: 'Sub-Saharan Africa',
  income_level: 'lower-middle'
}),
(c_ind:Country {
  code: 'IND',
  name: 'India',
  region: 'South Asia',
  income_level: 'lower-middle'
}),
(c_eth:Country {
  code: 'ETH',
  name: 'Ethiopia',
  region: 'Sub-Saharan Africa',
  income_level: 'low'
}),
(c_cod:Country {
  code: 'COD',
  name: 'DR Congo',
  region: 'Sub-Saharan Africa',
  income_level: 'low'
}),
(c_zaf:Country {
  code: 'ZAF',
  name: 'South Africa',
  region: 'Sub-Saharan Africa',
  income_level: 'upper-middle'
}),
(c_ken:Country {
  code: 'KEN',
  name: 'Kenya',
  region: 'Sub-Saharan Africa',
  income_level: 'lower-middle'
}),
(c_tza:Country {
  code: 'TZA',
  name: 'Tanzania',
  region: 'Sub-Saharan Africa',
  income_level: 'lower-middle'
}),
(c_rwa:Country {
  code: 'RWA',
  name: 'Rwanda',
  region: 'Sub-Saharan Africa',
  income_level: 'low'
}),

// --- Funding Areas ---
(f_hss:FundingArea {
  id: 'HSS',
  name: 'Health Systems Strengthening',
  budget_usd_millions: 150,
  fiscal_year: 2024
}),
(f_prev:FundingArea {
  id: 'PREV',
  name: 'Disease Prevention Programs',
  budget_usd_millions: 200,
  fiscal_year: 2024
}),
(f_gpe:FundingArea {
  id: 'GPE',
  name: 'Gender & Health Equity',
  budget_usd_millions: 50,
  fiscal_year: 2024
}),
(f_digi:FundingArea {
  id: 'DIGI',
  name: 'Digital Innovation & Data',
  budget_usd_millions: 75,
  fiscal_year: 2024
}),
(f_cap:FundingArea {
  id: 'CAPACITY',
  name: 'Capacity Building & Training',
  budget_usd_millions: 60,
  fiscal_year: 2024
}),

// ========================================
// RELATIONSHIPS
// ========================================

// --- COVERS_THEME: Document → Theme ---
// Global Health Strategy covers all 7 themes
(doc_gh)-[:COVERS_THEME {primary: true, weight: 95}]->(t_mnh),
(doc_gh)-[:COVERS_THEME {primary: true, weight: 90}]->(t_hiv),
(doc_gh)-[:COVERS_THEME {primary: true, weight: 85}]->(t_malaria),
(doc_gh)-[:COVERS_THEME {primary: true, weight: 80}]->(t_tb),
(doc_gh)-[:COVERS_THEME {primary: true, weight: 88}]->(t_vaccine),
(doc_gh)-[:COVERS_THEME {primary: false, weight: 70}]->(t_digital),
(doc_gh)-[:COVERS_THEME {primary: false, weight: 75}]->(t_gender),

// TB Elimination Plan covers TB and Vaccine Delivery
(doc_tb)-[:COVERS_THEME {primary: true, weight: 98}]->(t_tb),
(doc_tb)-[:COVERS_THEME {primary: false, weight: 60}]->(t_vaccine),

// Gender & Health Equity Framework covers Gender and MNH
(doc_ge)-[:COVERS_THEME {primary: true, weight: 95}]->(t_gender),
(doc_ge)-[:COVERS_THEME {primary: false, weight: 80}]->(t_mnh),

// --- MEASURED_BY: Theme → Indicator ---
(t_mnh)-[:MEASURED_BY {baseline: 223, target: 70, year: 2028}]->(i_mmr),
(t_mnh)-[:MEASURED_BY {baseline: 18, target: 12, year: 2028}]->(i_nmr),
(t_hiv)-[:MEASURED_BY {baseline: 76, target: 95, year: 2028}]->(i_art),
(t_malaria)-[:MEASURED_BY {baseline: 58, target: 25, year: 2028}]->(i_malaria_inc),
(t_tb)-[:MEASURED_BY {baseline: 86, target: 90, year: 2028}]->(i_tb_success),
(t_vaccine)-[:MEASURED_BY {baseline: 81, target: 90, year: 2028}]->(i_dtp3),
(t_vaccine)-[:MEASURED_BY {baseline: 83, target: 95, year: 2028}]->(i_mcv1),
(t_digital)-[:MEASURED_BY {baseline: 42, target: 75, year: 2028}]->(i_dhi),
(t_gender)-[:MEASURED_BY {baseline: 0.82, target: 1.0, year: 2028}]->(i_gdi),
(t_mnh)-[:MEASURED_BY {baseline: 0.8, target: 2.0, year: 2028}]->(i_facility),

// --- PRIORITY_IN: Theme → Country (with priority rank 1=highest) ---
// Maternal & Newborn Health priorities
(t_mnh)-[:PRIORITY_IN {rank: 1, rationale: 'Highest maternal mortality burden globally'}]->(c_nga),
(t_mnh)-[:PRIORITY_IN {rank: 1, rationale: 'Second highest absolute maternal deaths'}]->(c_ind),
(t_mnh)-[:PRIORITY_IN {rank: 2, rationale: 'High neonatal mortality rate'}]->(c_eth),
(t_mnh)-[:PRIORITY_IN {rank: 2, rationale: 'Significant maternal health gaps'}]->(c_cod),

// HIV/AIDS priorities
(t_hiv)-[:PRIORITY_IN {rank: 1, rationale: 'Largest HIV epidemic globally'}]->(c_zaf),
(t_hiv)-[:PRIORITY_IN {rank: 2, rationale: 'Growing epidemic, second most affected in East Africa'}]->(c_eth),
(t_hiv)-[:PRIORITY_IN {rank: 2, rationale: 'High prevalence in western Kenya'}]->(c_ken),

// Malaria priorities
(t_malaria)-[:PRIORITY_IN {rank: 1, rationale: 'Accounts for 27% of global malaria deaths'}]->(c_nga),
(t_malaria)-[:PRIORITY_IN {rank: 1, rationale: 'Second highest malaria burden'}]->(c_cod),
(t_malaria)-[:PRIORITY_IN {rank: 2, rationale: 'Significant malaria transmission zone'}]->(c_tza),

// TB priorities
(t_tb)-[:PRIORITY_IN {rank: 1, rationale: 'Highest TB incidence globally'}]->(c_ind),
(t_tb)-[:PRIORITY_IN {rank: 2, rationale: 'High TB-HIV co-infection rate'}]->(c_eth),
(t_tb)-[:PRIORITY_IN {rank: 2, rationale: 'Growing drug-resistant TB concern'}]->(c_ken),

// --- ALLOCATES_TO: FundingArea → Theme ---
(f_hss)-[:ALLOCATES_TO {amount_usd_millions: 80, percentage: 53}]->(t_mnh),
(f_hss)-[:ALLOCATES_TO {amount_usd_millions: 70, percentage: 47}]->(t_hiv),
(f_prev)-[:ALLOCATES_TO {amount_usd_millions: 90, percentage: 45}]->(t_malaria),
(f_prev)-[:ALLOCATES_TO {amount_usd_millions: 60, percentage: 30}]->(t_tb),
(f_prev)-[:ALLOCATES_TO {amount_usd_millions: 50, percentage: 25}]->(t_vaccine),
(f_gpe)-[:ALLOCATES_TO {amount_usd_millions: 30, percentage: 60}]->(t_gender),
(f_gpe)-[:ALLOCATES_TO {amount_usd_millions: 20, percentage: 40}]->(t_mnh),
(f_digi)-[:ALLOCATES_TO {amount_usd_millions: 75, percentage: 100}]->(t_digital),
(f_cap)-[:ALLOCATES_TO {amount_usd_millions: 35, percentage: 58}]->(t_mnh),
(f_cap)-[:ALLOCATES_TO {amount_usd_millions: 25, percentage: 42}]->(t_hiv),

// --- SUPPORTS_THEME: Country → Theme (implementation partnerships) ---
(c_nga)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 65}]->(t_mnh),
(c_nga)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 70}]->(t_malaria),
(c_ind)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 72}]->(t_tb),
(c_ind)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 60}]->(t_mnh),
(c_eth)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 55}]->(t_hiv),
(c_eth)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 58}]->(t_mnh),
(c_zaf)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 78}]->(t_hiv),
(c_ken)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 68}]->(t_hiv),
(c_ken)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 62}]->(t_tb),
(c_rwa)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 85}]->(t_digital),
(c_tza)-[:SUPPORTS_THEME {implementation_status: 'active', progress_pct: 60}]->(t_malaria);
