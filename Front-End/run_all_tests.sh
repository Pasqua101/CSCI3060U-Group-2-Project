#!/bin/bash

FRONT_END_EXE="main.py" 
FIXTURES_DIR="fixtures/current_accounts.txt"
TESTS_BASE_DIR="tests"

echo "Starting Team Banking System Test Suite (Modular Architecture)..."

for trans_dir in "$TESTS_BASE_DIR"/*/; do
    category=$(basename "$trans_dir")
    echo "Processing Category: $category"
    
    ACTUAL_OUT_DIR="${trans_dir}actual_outputs"
    mkdir -p "$ACTUAL_OUT_DIR"
    
    for input_file in "$trans_dir"inputs/*.in.txt; do
        [ -e "$input_file" ] || continue
        
        base_name=$(basename "$input_file" .in.txt)
        actual_output="$ACTUAL_OUT_DIR/${base_name}.actual.transactions.txt"
        
        echo "  Running Test: $base_name"
        
        python3 "$FRONT_END_EXE" "$FIXTURES_DIR" "temp_daily.txt" < "$input_file" > "$actual_output"
        
        expected_output="${trans_dir}expected_outputs/${base_name}.expected.transactions.txt"
        
        if [ -f "$expected_output" ]; then
            if diff -Z --strip-trailing-cr -q "$expected_output" "$actual_output" > /dev/null; then
                echo "    RESULT: PASS"
            else
                echo "    RESULT: FAIL (Differences found)"
            fi
        else
            echo "    RESULT: SKIPPED (Expected output file not found)"
        fi
    done
done

echo "Batch execution complete."