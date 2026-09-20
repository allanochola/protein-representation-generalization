"""Synthetic A2-C audit. No real family geometry is computed."""
import ast
import importlib.util
from pathlib import Path
EXP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("a2c_synthetic",EXP/"run_gate_a2_geometry.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def require(ok,message):
    if not ok: raise RuntimeError(message)
def rejects(fn):
    try: fn()
    except RuntimeError: return
    raise RuntimeError("Invalid synthetic case was accepted")
require(m.A2_CENSUS_AUTHORIZED is False,"Census must be disabled")
require(not m.OUTPUT.exists(),"Geometry output already exists")
for filename,gate in (("run_gate_a2_scan.py","A2_SCAN_AUTHORIZED"),
                      ("run_gate_a2_sequence_recovery.py","A2_SEQUENCE_RECOVERY_AUTHORIZED")):
    t=ast.parse((EXP/filename).read_bytes())
    values=[ast.literal_eval(n.value) for n in ast.walk(t) if isinstance(n,ast.Assign)
            and any(isinstance(x,ast.Name) and x.id==gate for x in n.targets)]
    require(values==[False],"Previous phase is not closed")
require(m.family_token("PF00001.7",{"PF00001":""})=="PF00001","Empty clan fallback")
require(m.family_token("PF00001.7",{"PF00001":"CL0001"})=="CL0001","Clan precedence")
rejects(lambda:m.family_token("PF99999",{"PF00001":""}))
def rec(universe,label,s):
    return {"universe":universe,"class_name":label,"sequence_sha256":s}
metadata={"d1":rec("discovery","positive","a"),"dn":rec("discovery","negative","b"),
          "c1":rec("confirmatory","positive","c"),"cn":rec("confirmatory","negative","d"),
          "c2":rec("confirmatory","positive","e"),"cn2":rec("confirmatory","negative","a")}
clusters={"d1":"S1","dn":"S1","c1":"S2","cn":"S3","c2":"S4","cn2":"S5"}
tokens={"d1":set(),"dn":{"CL1"},"c1":{"CL1","CL2"},"cn":{"CL1","CL2"},"c2":set(),"cn2":set()}
a,c,p,s=m.geometry(metadata,clusters,tokens)
require(a["d1"]==a["dn"]==a["c1"]==a["cn"],"Mixed-label transitive bridge lost")
require(a["c2"]!=a["c1"] and a["cn2"]!=a["c1"],"Unsupported singleton merged")
require(s["populations"]["confirmatory_negative"]["bearing_component_count"]==2,"Negative intersections")
require(s["populations"]["confirmatory_negative"]["largest_intersection_share"]==0.5,"Negative denominator")
require(s["confirmatory_positive_disjointness"]["records_sharing_discovery_positive_component"]==1,"Discovery bridge")
require(s["direct_cross_label_pfam_relationships"]["confirmatory_only"]==
        {"unique_pair_count":1,"pair_token_incidence_count":2},"Pair multiplicity semantics")
require(s["exact_sequence_identity_across_universes"]=={"pair_count":1,"confirmatory_record_count":1},"Exact sequence identity")
reverse=lambda d:dict(reversed(list(d.items())))
require(m.geometry(reverse(metadata),reverse(clusters),reverse(tokens))== (a,c,p,s),"Input order dependence")
rejects(lambda:m.geometry(metadata,{k:v for k,v in clusters.items() if k!="c1"},tokens))
bad=dict(tokens);bad["c1"]={""}
rejects(lambda:m.geometry(metadata,clusters,bad))
rejects(lambda:m.check_columns(["model_score"]))
# Verify input byte identities without invoking load_inputs or geometry on real data.
require(m.sha(m.CONTRACT.read_bytes())==m.CONTRACT_SHA256,"Contract identity")
print("PASS — disabled gates; clan fallback; mixed-label closure and negative denominators")
print("PASS — cross-label pair multiplicity; exact identity; deterministic serialization inputs")
print("PASS — malformed inputs rejected; contract bound to runner")
print("Real family geometry computed: NO")
