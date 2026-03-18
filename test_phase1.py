"""Test rápido de todos los módulos de la Fase 1."""
import sys
sys.path.insert(0, ".")

# Test 1: Models
from app.models.prospect import Prospect
from app.models.competitor import COMPETITORS, detect_competitor
from app.models.pipeline import PIPELINE_STAGES

p = Prospect.create_from_input("Bright Smile Dental, Austin TX")
print(f"✅ Prospect: {p.id} → {p.clinic_name}")

c = detect_competitor("dentrix")
print(f"✅ Competitor: {c[1]['name'] if c else 'None'}")

print(f"✅ Pipeline: {[s.label for s in PIPELINE_STAGES]}")

# Test 2: Utils
from app.utils.json_parser import parse_llm_json, create_research_fallback

raw = '```json\n{"fit_score": 8, "clinic_name": "Test"}\n```'
parsed = parse_llm_json(raw)
print(f"✅ JSON Parser: {parsed}")

fb = create_research_fallback("Test Dental, TX")
print(f"✅ Research Fallback: {fb['clinic_name']}, score={fb['fit_score']}")

from app.utils.logger import LogAccumulator
log = LogAccumulator()
log.add("start", "Test log entry")
log.add("success", "All good!")
print(f"✅ Logger:\n{log.text}")

# Test 3: Agents
from app.agents.prompts import build_research_query
q = build_research_query("Bright Smile Dental, Austin TX", "name")
print(f"✅ Query builder: {q[:60]}...")

# Test 4: Services - Storage
from app.services.storage_service import StorageService
store = StorageService(storage_path="")  # Sin auto-save
store.add_prospect(p)
metrics = store.get_pipeline_metrics()
print(f"✅ Storage: {metrics}")

print("\n🏁 Todos los módulos de la Fase 1 funcionan correctamente.")
