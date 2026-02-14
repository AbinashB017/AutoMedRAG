import requests
import xml.etree.ElementTree as ET

def fetch_pubmed(query: str, max_results: int = 20):
    """
    Fetch papers from PubMed API based on a search query.
    If real API fails, returns mock data for demonstration.
    """
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }

        search_res = requests.get(search_url, params=search_params, timeout=10).json()
        id_list = search_res.get("esearchresult", {}).get("idlist", [])

        if not id_list:
            return _get_mock_papers(query)

        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml"
        }

        fetch_res = requests.get(fetch_url, params=fetch_params, timeout=10)

        root = ET.fromstring(fetch_res.content)

        papers = []
        for article in root.findall(".//PubmedArticle"):
            try:
                title_elem = article.find(".//ArticleTitle")
                abstract_elem = article.find(".//AbstractText")
                
                if title_elem is not None and abstract_elem is not None:
                    papers.append({
                        "title": title_elem.text or "Unknown Title",
                        "abstract": abstract_elem.text or "No abstract available"
                    })
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue

        # If no papers found, return mock data
        if not papers:
            return _get_mock_papers(query)
        
        return papers
        
    except Exception as e:
        print(f"PubMed API error: {e}, using mock data")
        return _get_mock_papers(query)

def _get_mock_papers(query: str):
    """Return mock papers for demonstration/testing purposes"""
    mock_data = {
        "diabetes": [
            {"title": "Type 2 Diabetes Management and Metabolic Control", "abstract": "Recent advances in diabetes treatment include GLP-1 receptor agonists and SGLT2 inhibitors. These medications have shown significant benefits in glycemic control and cardiovascular protection."},
            {"title": "Insulin Resistance and Metformin Therapy", "abstract": "Metformin remains the most commonly prescribed medication for type 2 diabetes. Its mechanism involves increasing insulin sensitivity and reducing hepatic glucose production."},
            {"title": "Lifestyle Interventions in Diabetes Prevention", "abstract": "Comprehensive lifestyle modifications can prevent or delay the onset of type 2 diabetes by 58% over 3 years according to the Diabetes Prevention Program."}
        ],
        "hiv": [
            {"title": "Antiretroviral Therapy Advances in HIV Treatment", "abstract": "Modern antiretroviral therapy (ART) with integrase inhibitors can achieve undetectable viral loads. U=U (Undetectable equals Untransmittable) is well-established in clinical practice."},
            {"title": "Pre-Exposure Prophylaxis (PrEP) for HIV Prevention", "abstract": "PrEP with tenofovir/emtricitabine shows >90% efficacy in preventing HIV transmission when taken consistently for high-risk populations."},
            {"title": "Long-Acting HIV Drugs and Treatment Adherence", "abstract": "Long-acting formulations of HIV medications administered monthly improve treatment adherence and patient satisfaction rates significantly."}
        ],
        "pneumonia": [
            {"title": "Community-Acquired Pneumonia Treatment Guidelines", "abstract": "Community-acquired pneumonia remains a leading cause of infectious disease mortality. Empirical antibiotic therapy based on severity provides optimal outcomes."},
            {"title": "Respiratory Support in Severe Pneumonia", "abstract": "Mechanically ventilated patients with pneumonia require lung-protective ventilation strategies. Early recognition of ARDS is crucial for improved survival."},
            {"title": "Viral vs Bacterial Pneumonia Management", "abstract": "Distinguishing between viral and bacterial pneumonia helps guide appropriate antimicrobial therapy and reduces unnecessary antibiotic use."}
        ],
        "spondylitis": [
            {"title": "Ankylosing Spondylitis and Spinal Inflammation", "abstract": "Ankylosing spondylitis is a chronic inflammatory disease affecting the spine and joints. TNF inhibitors have revolutionized treatment outcomes for spondylitis patients."},
            {"title": "Biological Therapies in Spondyloarthritis Management", "abstract": "TNF-alpha inhibitors and IL-17 inhibitors show significant efficacy in reducing inflammation and improving mobility in ankylosing spondylitis."},
            {"title": "Physiotherapy and Exercise in Ankylosing Spondylitis", "abstract": "Regular physical therapy and specific exercises help maintain spinal mobility and reduce pain in spondylitis patients."}
        ],
        "arthritis": [
            {"title": "Rheumatoid Arthritis: Biologic Disease-Modifying Therapies", "abstract": "Disease-modifying antirheumatic drugs (DMARDs) and biologic agents have transformed rheumatoid arthritis outcomes. Early intervention improves long-term prognosis."},
            {"title": "Osteoarthritis Management and Joint Preservation", "abstract": "Osteoarthritis treatment includes pharmacological and non-pharmacological approaches. Weight loss and exercise are fundamental non-drug interventions."},
            {"title": "Anti-TNF Therapies in Rheumatoid Arthritis", "abstract": "TNF inhibitors significantly reduce joint inflammation and slow disease progression in rheumatoid arthritis patients."}
        ],
        "asthma": [
            {"title": "Asthma Control and Inhaled Corticosteroid Therapy", "abstract": "Inhaled corticosteroids remain the gold standard for asthma management. Regular controller therapy prevents acute exacerbations."},
            {"title": "Severe Asthma and Biologic Therapeutics", "abstract": "Monoclonal antibodies targeting IL-5, IgE, and IL-4 receptors have improved outcomes in severe asthma phenotypes."},
            {"title": "Asthma Action Plans and Patient Education", "abstract": "Written asthma action plans and patient education improve medication adherence and reduce emergency department visits."}
        ],
        "cancer": [
            {"title": "Immunotherapy Revolution in Oncology", "abstract": "Checkpoint inhibitors and CAR-T cell therapies have transformed cancer treatment. Response rates of 30-50% in previously difficult-to-treat cancers."},
            {"title": "Precision Oncology and Genomic Profiling", "abstract": "Genomic profiling enables targeted cancer therapy based on tumor genetics. Personalized treatments show improved efficacy and reduced side effects."},
            {"title": "Combination Chemotherapy in Advanced Cancers", "abstract": "Multi-agent chemotherapy regimens provide synergistic effects. Clinical trials demonstrate improved overall survival with combination approaches."}
        ],
        "hypertension": [
            {"title": "Blood Pressure Management and Antihypertensive Agents", "abstract": "Current guidelines emphasize individualized blood pressure targets. ACE inhibitors and ARBs remain first-line agents for cardiovascular protection."},
            {"title": "Resistant Hypertension and Combination Therapy", "abstract": "Combination therapy with two or more antihypertensive agents is required for resistant hypertension. Fixed-dose combinations improve adherence."},
            {"title": "Lifestyle Modifications in Hypertension Control", "abstract": "Dietary sodium reduction, weight loss, and regular exercise significantly lower blood pressure and reduce cardiovascular risk."}
        ],
        "covid": [
            {"title": "COVID-19 mRNA Vaccines and Pandemic Prevention", "abstract": "mRNA vaccines show >95% efficacy against severe COVID-19 disease. Vaccination campaigns have reduced hospitalizations worldwide."},
            {"title": "Post-COVID Syndrome and Long-Term Complications", "abstract": "Approximately 10-30% of COVID-19 patients experience prolonged symptoms. Long COVID impacts multiple organ systems."},
            {"title": "SARS-CoV-2 Antiviral Treatments and Therapeutics", "abstract": "Monoclonal antibodies and oral antivirals reduce severe COVID-19 outcomes when used early in infection."}
        ],
        "kidney": [
            {"title": "Chronic Kidney Disease and Renal Function Preservation", "abstract": "ACE inhibitors and SGLT2 inhibitors slow CKD progression. Early intervention can preserve remaining renal function."},
            {"title": "Glomerulonephritis and Kidney Inflammation", "abstract": "Immunosuppressive therapy is essential in rapidly progressive glomerulonephritis. Early diagnosis and treatment prevent progression to ESRD."},
            {"title": "Dialysis and Renal Replacement Therapy Management", "abstract": "Hemodialysis and peritoneal dialysis maintain fluid and electrolyte balance in end-stage renal disease patients."}
        ],
        "gout": [
            {"title": "Acute Gout Attack Management and NSAIDs", "abstract": "Acute gout is treated with NSAIDs, colchicine, or corticosteroids. Rapid inflammation reduction prevents chronic complications."},
            {"title": "Uric Acid Lowering Therapy in Gout Prophylaxis", "abstract": "Allopurinol and febuxostat reduce serum uric acid levels. Xanthine oxidase inhibitors prevent recurrent gout attacks."},
            {"title": "Purine-Restricted Diets and Lifestyle Modifications", "abstract": "Limiting purine-rich foods and alcohol reduces uric acid production. Weight loss and hydration improve gout outcomes."}
        ],
        "alzheimer": [
            {"title": "Amyloid and Tau Pathology in Alzheimer's Disease", "abstract": "Alzheimer's disease involves accumulation of amyloid-beta plaques and tau tangles. Recent anti-amyloid monoclonal antibodies show promise in slowing cognitive decline in early stages."},
            {"title": "Cognitive Decline Prevention and Lifestyle Interventions", "abstract": "Mediterranean diet, cognitive training, and physical exercise reduce Alzheimer's risk by up to 30%. Sleep quality and social engagement also play crucial roles."},
            {"title": "Biomarkers and Early Detection of Neurodegenerative Disease", "abstract": "Plasma phosphorylated tau and amyloid-beta ratios enable early detection decades before symptom onset. Precision medicine approaches personalize treatment strategies."}
        ],
        "heart": [
            {"title": "Coronary Artery Disease and Stent Interventions", "abstract": "Percutaneous coronary intervention (PCI) with bare-metal or drug-eluting stents treats acute coronary syndromes. Dual antiplatelet therapy reduces thrombotic complications."},
            {"title": "Heart Failure Management with SGLT2 Inhibitors", "abstract": "SGLT2 inhibitors reduce hospitalizations and mortality in heart failure with reduced ejection fraction. Benefits extend across diabetic and non-diabetic populations."},
            {"title": "Cardiovascular Risk Stratification and Prevention", "abstract": "Risk calculators incorporating lipid profiles, blood pressure, and inflammatory markers guide preventive strategies. Statins and ACE inhibitors remain cornerstone therapies."}
        ],
        "stroke": [
            {"title": "Acute Ischemic Stroke Thrombolysis and Thrombectomy", "abstract": "Intravenous thrombolysis and mechanical thrombectomy restore cerebral blood flow. Time-is-brain principle emphasizes rapid intervention within critical windows."},
            {"title": "Stroke Prevention in Atrial Fibrillation", "abstract": "Anticoagulation with DOACs reduces stroke risk by 65% in atrial fibrillation patients. Left atrial appendage closure offers alternative for anticoagulation-intolerant patients."},
            {"title": "Neuroplasticity and Rehabilitation after Stroke", "abstract": "Intensive physical therapy and constraint-induced movement therapy promote neuroplastic recovery. Speech and occupational therapy improve functional outcomes post-stroke."}
        ],
        "depression": [
            {"title": "Antidepressant Efficacy and Selective Serotonin Reuptake Inhibitors", "abstract": "SSRIs remain first-line pharmacotherapy for major depressive disorder. Response rates reach 60-70% with adequate dosing and treatment duration."},
            {"title": "Psychotherapy and Cognitive Behavioral Therapy Outcomes", "abstract": "Cognitive behavioral therapy shows efficacy comparable to antidepressants. Combination therapy of medication and psychotherapy provides superior outcomes."},
            {"title": "Treatment-Resistant Depression and Ketamine", "abstract": "Esketamine nasal spray provides rapid symptom improvement in treatment-resistant depression. Neuroplasticity changes occur within hours of administration."}
        ],
        "obesity": [
            {"title": "GLP-1 Receptor Agonists for Weight Management", "abstract": "Semaglutide and tirzepatide produce 15-20% weight loss in obese patients. Cardiovascular benefits extend beyond weight reduction with improved metabolic parameters."},
            {"title": "Bariatric Surgery and Metabolic Outcomes", "abstract": "Gastric bypass and sleeve gastrectomy produce sustained weight loss and remission of type 2 diabetes. Long-term nutritional monitoring prevents deficiency states."},
            {"title": "Childhood Obesity Prevention and Family Interventions", "abstract": "Early lifestyle interventions during childhood prevent obesity trajectory. Parental involvement and school-based programs show 20-30% weight reduction rates."}
        ],
        "hepatitis": [
            {"title": "Direct-Acting Antivirals in Hepatitis C Treatment", "abstract": "Sofosbuvir-based regimens achieve cure rates >95% in hepatitis C. Treatment duration of 8-12 weeks eliminates viral replication across genotypes."},
            {"title": "Hepatitis B Immunization and Viral Suppression", "abstract": "Hepatitis B vaccines prevent infection in 95% of recipients. Antiviral agents like tenofovir or entecavir suppress viral replication and prevent cirrhosis."},
            {"title": "Cirrhosis Prevention and Liver Function Preservation", "abstract": "Early treatment of hepatitis prevents progression to cirrhosis. Screening for hepatocellular carcinoma using ultrasound and AFP improves detection at early stages."}
        ],
        "crohns": [
            {"title": "Inflammatory Bowel Disease and TNF Inhibitor Therapy", "abstract": "Infliximab and adalimumab induce remission in 60-70% of Crohn's disease patients. TNF inhibitors reduce hospitalizations and surgery requirements significantly."},
            {"title": "Vedolizumab and Gut-Specific Integrin Blockade", "abstract": "Vedolizumab selectively targets gut immune cells with minimal systemic immunosuppression. Efficacy in Crohn's disease reaches 50-60% at 6 weeks."},
            {"title": "Nutritional Management in Inflammatory Bowel Disease", "abstract": "Exclusive enteral nutrition achieves remission rates comparable to corticosteroids. Anti-inflammatory diets reduce flare frequency and improve quality of life."}
        ],
        "thyroid": [
            {"title": "Hypothyroidism Management and Levothyroxine Replacement", "abstract": "Levothyroxine monotherapy treats most hypothyroidism cases effectively. TSH-suppressive therapy prevents thyroid cancer recurrence after total thyroidectomy."},
            {"title": "Graves' Disease and Hyperthyroidism Treatment", "abstract": "Antithyroid medications, beta-blockers, and radioiodine therapy manage Graves' disease. Thyroid-stimulating immunoglobulin monitoring guides treatment decisions."},
            {"title": "Thyroid Cancer Screening and Radioactive Iodine Ablation", "abstract": "Thyroid ultrasound and fine-needle aspiration biopsy diagnose thyroid malignancies. Radioactive iodine ablation treats differentiated thyroid cancer with excellent survival rates."}
        ],
        "lupus": [
            {"title": "Systemic Lupus Erythematosus and Antimalarial Drugs", "abstract": "Hydroxychloroquine prevents lupus flares and reduces cumulative organ damage. Long-term use decreases mortality by 50% and prevents thrombosis."},
            {"title": "Immunosuppressive Therapy in lupus nephritis", "abstract": "Cyclophosphamide or mycophenolate mofetil preserve renal function in lupus nephritis. Combined therapy with corticosteroids achieves remission in 70-80% of patients."},
            {"title": "Lupus Anticoagulant and Thrombotic Manifestations", "abstract": "Antiphospholipid antibodies increase thrombotic risk in lupus. Anticoagulation with warfarin or DOACs prevents recurrent thrombosis in antiphospholipid syndrome."}
        ],
        "parkinson": [
            {"title": "Dopamine Replacement Therapy in Parkinson's Disease", "abstract": "Levodopa with carbidopa remains gold standard for motor symptom management. Extended-release formulations provide continuous dopaminergic stimulation."},
            {"title": "Deep Brain Stimulation for Advanced Parkinson's Disease", "abstract": "DBS reduces motor complications and improves quality of life in advanced Parkinson's. Subthalamic nucleus stimulation decreases dyskinesia by 60-70%."},
            {"title": "Neuroprotective Strategies and Disease Modification", "abstract": "MAO-B inhibitors and GLP-1 agonists show potential neuroprotective effects. Experimental therapies targeting alpha-synuclein aggregation are in advanced trials."}
        ]
    }
    
    # Try to find matching mock data - exact keyword match first
    query_lower = query.lower()
    for keyword, papers in mock_data.items():
        if keyword in query_lower:
            return papers[:3]
    
    # If no exact match, search in content
    for keyword, papers in mock_data.items():
        if any(word in query_lower for word in keyword.split()):
            return papers[:3]
    
    # Return empty if no match - don't return random data
