awk '{print $0"&inform(added)"}' ./test-conc_das.txt \
    | paste -d "|" - ./test_surface_forms_Tue19May_1118/test-eval.txt \
    | sort -R \
    | sed "s/inform(//g" \
    | sed "s/)//g" \
    | sed "s/&/, ,/g" \
    | sed G \
    | sed "s/|/\n/" \
    | head -n 300 \
    > surface_forms_manual_analysis.txt

awk '{print $0"&inform(added)"}' ./test-conc_das.txt \
    | paste -d "|" - ./test_baseline_Tue19May_1115/test-eval.txt \
    | sort -R \
    | sed "s/inform(//g" \
    | sed "s/)//g" \
    | sed "s/&/, ,/g" \
    | sed G \
    | sed "s/|/\n/" \
    | head -n 300 \
    > baseline_manual_analysis.txt