# External E2E run 34074537547 failure diagnosis

This file is an execution diagnostic only. It does not alter Protocol A.1, codec settings, tolerance ladders, eligibility, early stopping, failure semantics, or the frozen 63-system confirmatory cohort.

## Shard 2 material-level failures
```csv
material_id,error_type,error
aflow-Cl1O12Pb5V3_ICSD_203074,HTTPError,HTTP Error 500: INTERNAL SERVER ERROR
```

## Shard 2 row-level failures
```csv
material_id,corpus,domain,ladder,codec,nominal_tolerance_relative,stage,category,detail
nomad2d-1_3Aeqri4-hc,external,vacuum2d,base,ZFP,0.03,zfp@0.03:resolved_bader,bader_solver_failure,IndexError: index 3 is out of bounds for axis 0 with size 3
nomad2d-1_3Aeqri4-hc,external,vacuum2d,base,ZFP,0.1,zfp@0.1:resolved_bader,bader_solver_failure,IndexError: index 4 is out of bounds for axis 1 with size 3
```

## Shard 2 summary
```json
{
  "n_materials_selected": 8,
  "n_materials_complete": 7,
  "n_material_failures": 1,
  "n_row_failures": 2,
  "n_rows_retained": 174,
  "all_codec_bounds_respected": true,
  "n_tight_eligible_materials": 4,
  "n_certified_at_1e-4": 31,
  "n_certified_at_1e-3": 73,
  "n_certified_at_1e-2": 124,
  "n_maxima_count_changes": 72,
  "median_realized_Linf_over_nominal_by_codec": {
    "ZFP": 0.14961131539047057,
    "SZ3": 0.999997552915521,
    "SPERR": 0.9999733646556648
  },
  "material_failure_ids": [
    "aflow-Cl1O12Pb5V3_ICSD_203074"
  ],
  "row_failure_ids": [
    "nomad2d-1_3Aeqri4-hc"
  ]
}```

## Shard 2 material audit
```csv
material_id,domain,stability_floor_A1_e,tight_enabled,n_row_attempts,n_rows_computed,n_rows_retained,n_row_failures,n_early_stop_boundaries,n_rows_dropped_post_early_stop,status
aflow-Ca1O4U1_ICSD_246962,bulk,0.0003760203896474,True,32,32,32,0,3,0,COMPLETE
aflow-B0.667N0.667_ICSD_162872,bulk,8.16104046563737e-07,True,37,37,37,0,2,0,COMPLETE
aflow-H3Ni1Zr1_ICSD_658750,bulk,0.0061509244098267,False,19,19,19,0,3,0,COMPLETE
aflow-Cl1O12Pb5V3_ICSD_203074,bulk,0.0035547402881945,,0,0,0,0,0,0,PIPELINE_FAILURE
aflow-Na10Sn12Yb1_ICSD_172210,bulk,0.0692420429013118,False,4,4,4,0,3,0,COMPLETE
nomad2d-03AViAQBOpvV,vacuum2d,0.0005582175965566,True,31,31,31,0,3,0,COMPLETE
nomad2d-1_3Aeqri4-hc,vacuum2d,0.0012802870748647,False,20,18,18,2,2,0,COMPLETE
nomad2d-3I6dBXihz7G1,vacuum2d,2.40716655017792e-05,True,33,33,33,0,3,0,COMPLETE
```
